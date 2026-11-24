import asyncio
import httpx
from typing import Any, Dict, Optional
from src.utils.logger import get_logger


class CryptoAPIClient:
    """
    Cliente asíncrono encargado únicamente de la comunicación HTTP con la API.
    Implementa manejo diferenciado de errores transitorios vs. permanentes.
    """

    def __init__(self, base_url: str, timeout: float = 10.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger(self.__class__.__name__)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "CryptoAPIClient":
        """Inicializa la sesión asíncrona reutilizable al entrar en el bloque 'async with'."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={"Accept": "application/json", "User-Agent": "AI-Automation-Ingestor/1.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cierra ordenadamente la sesión HTTP al salir."""
        if self._client:
            await self._client.aclose()

    async def fetch_coin_market(self, coin_id: str, vs_currency: str = "usd") -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de mercado de una criptomoneda de forma asíncrona.
        Diferencia errores transitorios (reintenta) de errores permanentes (aborta ese recurso).
        """
        if not self._client:
            raise RuntimeError("El cliente debe usarse dentro de un contexto 'async with'.")

        endpoint = "/coins/markets"
        params = {"vs_currency": vs_currency, "ids": coin_id}

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"[{coin_id}] Solicitando datos (Intento {attempt}/{self.max_retries})...")
                response = await self._client.get(endpoint, params=params)
                response.raise_for_status()

                data = response.json()
                if not data:
                    # Error permanente lógico: la API respondió 200 OK pero la moneda no existe
                    self.logger.error(
                        f"[{coin_id}] ERROR PERMANENTE: Recurso no encontrado o ID inválido (lista vacía)."
                    )
                    return None

                self.logger.info(f"[{coin_id}] Descarga exitosa.")
                return data[0]

            # --- 1. ERRORES TRANSITORIOS (Vale la pena reintentar) ---
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                self.logger.warning(
                    f"[{coin_id}] ERROR TRANSITORIO de red/timeout ({type(e).__name__}). Reintentando..."
                )

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code

                # 429 (Rate Limit) o 5xx (Error interno del servidor remoto) -> Transitorios
                if status_code == 429 or status_code >= 500:
                    self.logger.warning(
                        f"[{coin_id}] ERROR TRANSITORIO HTTP {status_code}. Esperando antes de reintentar..."
                    )
                # --- 2. ERRORES PERMANENTES (No tiene sentido reintentar) ---
                else:
                    # Ej: 400 Bad Request, 401/403 API Key inválida, 404 Not Found
                    self.logger.error(
                        f"[{coin_id}] ERROR PERMANENTE HTTP {status_code}: {e.response.text[:120]}. Abortando recurso."
                    )
                    return None

            except Exception as e:
                self.logger.error(f"[{coin_id}] Error inesperado no controlado: {e}")
                return None

            # Espera progresiva (Backoff) antes del siguiente intento transitorio
            if attempt < self.max_retries:
                await asyncio.sleep(2 * attempt)

        self.logger.error(f"[{coin_id}] Se agotaron los {self.max_retries} reintentos por fallos transitorios.")
        return None
