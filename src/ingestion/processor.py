import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from src.utils.logger import get_logger


class MarketDataProcessor:
    """
    Clase desacoplada encargada exclusivamente de parsear, limpiar y persistir
    los datos obtenidos por el cliente de ingesta.
    """

    def __init__(self, output_dir: str = "data"):
        project_root = Path(__file__).resolve().parents[2]
        self.output_dir = project_root / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(self.__class__.__name__)

    def parse_records(self, raw_results: List[Optional[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Filtra respuestas fallidas (None) y extrae un esquema limpio y estructurado."""
        clean_records = []
        ingested_at = datetime.now(timezone.utc).isoformat()

        for item in raw_results:
            if not item:
                continue

            clean_records.append(
                {
                    "id": item.get("id"),
                    "symbol": str(item.get("symbol", "")).upper(),
                    "name": item.get("name"),
                    "current_price_usd": item.get("current_price"),
                    "market_cap_usd": item.get("market_cap"),
                    "total_volume_24h": item.get("total_volume"),
                    "price_change_pct_24h": item.get("price_change_percentage_24h"),
                    "last_updated_api": item.get("last_updated"),
                    "ingested_at_utc": ingested_at,
                }
            )

        self.logger.info(f"Parseo completado: {len(clean_records)} registros válidos procesados.")
        return clean_records

    def save_to_storage(self, clean_records: List[Dict[str, Any]]) -> Optional[Path]:
        """Guarda los registros limpios en formato CSV dentro de data/."""
        if not clean_records:
            self.logger.warning("No hay registros válidos para guardar en almacenamiento.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.output_dir / f"crypto_market_{timestamp}.csv"

        df = pd.DataFrame(clean_records)
        df.to_csv(csv_path, index=False, encoding="utf-8")

        self.logger.info(f"Datos guardados exitosamente en: {csv_path}")
        return csv_path
