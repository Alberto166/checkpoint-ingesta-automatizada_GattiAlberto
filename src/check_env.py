import os
import platform
import sys
from pathlib import Path
from dotenv import load_dotenv

def verificar_entorno():
    print("=" * 50)
    print(" VALIDACIÓN DE ENTORNO - DEV CONTAINER")
    print("=" * 50)

    # 1. Verificar versión de Python y Sistema Operativo
    print(f" Versión de Python: {sys.version.split()[0]}")
    print(f" Sistema Operativo del contenedor: {platform.system()} ({platform.release()})")
    print(f" Directorio actual de trabajo: {os.getcwd()}")

    # 2. Cargar variables de entorno usando rutas relativas a la raíz
    raiz_proyecto = Path(__file__).resolve().parent.parent
    ruta_env = raiz_proyecto / ".env.example"

    if ruta_env.exists():
        load_dotenv(dotenv_path=ruta_env)
        print(f"\n Archivo de configuración encontrado en: {ruta_env.name}")
        
        # 3. Comprobar lectura de variables
        openai_key = os.getenv("OPENAI_API_KEY")
        mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
        db_url = os.getenv("DATABASE_URL")

        print(f"   - OPENAI_API_KEY: {openai_key}")
        print(f"   - MLFLOW_TRACKING_URI: {mlflow_uri}")
        print(f"   - DATABASE_URL: {db_url}")
    else:
        print("\n Error: No se encontró el archivo .env.example")

    print("=" * 50)

if __name__ == "__main__":
    verificar_entorno()

