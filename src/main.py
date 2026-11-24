import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion.client import CryptoAPIClient
from src.ingestion.processor import MarketDataProcessor
from src.utils.logger import get_logger


async def run_ingestion_pipeline() -> None:
    """
    Orquesta el flujo completo de ingesta asíncrona:
    1. Carga configuración desde .env
    2. Ejecuta múltiples peticiones concurrentes con asyncio.gather()
    3. Procesa y almacena los resultados válidos de forma desacoplada
    """
    logger = get_logger("Orchestrator")

    # Cargar variables de entorno desde la raíz del proyecto
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=project_root / ".env")

    base_url = os.getenv("API_BASE_URL", "https://api.coingecko.com/api/v3")
    timeout = float(os.getenv("REQUEST_TIMEOUT", "10.0"))

    # Lista de recursos a consultar en paralelo.
    # Incluimos 'moneda-inexistente-xyz' para demostrar resiliencia ante errores permanentes.
    target_coins = [
        "bitcoin",
        "ethereum",
        "solana",
        "cardano",
        "ripple",
        "moneda-inexistente-xyz",
    ]

    logger.info(f"Iniciando pipeline de ingesta concurrente para {len(target_coins)} recursos...")
    start_time = time.perf_counter()

    # 1. Fase de Extracción (Concurrente)
    async with CryptoAPIClient(base_url=base_url, timeout=timeout) as client:
        tasks = [client.fetch_coin_market(coin) for coin in target_coins]
        raw_results = await asyncio.gather(*tasks)

    # 2. Fase de Transformación y Almacenamiento (Desacoplada)
    processor = MarketDataProcessor(output_dir="data")
    clean_records = processor.parse_records(raw_results)
    output_file = processor.save_to_storage(clean_records)

    elapsed_time = time.perf_counter() - start_time
    logger.info(
        f"Pipeline finalizado en {elapsed_time:.2f} segundos. "
        f"Exitosos: {len(clean_records)}/{len(target_coins)} | Archivo: {output_file}"
    )


if __name__ == "__main__":
    asyncio.run(run_ingestion_pipeline())
