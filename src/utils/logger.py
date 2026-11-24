import logging
import sys
from pathlib import Path


def get_logger(name: str, log_file: str = "ingestion.log") -> logging.Logger:
    """
    Configura y devuelve un logger estructurado que escribe tanto en consola
    como en un archivo dentro de la carpeta logs/ del proyecto.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si se llama varias veces al mismo logger
    if logger.handlers:
        return logger

    # Formato estructurado: Timestamp | Nivel | Módulo | Mensaje
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Handler para mostrar en consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Handler para guardar en archivo (logs/ingestion.log)
    # Subimos 2 niveles desde src/utils/logger.py para llegar a la raíz del proyecto
    project_root = Path(__file__).resolve().parents[2]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(logs_dir / log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
