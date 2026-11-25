import os
import platform
import sys
from pathlib import Path
from dotenv import load_dotenv


def verificar_entorno() -> None:
    print("=" * 55)
    print(" VALIDACIÓN DE ENTORNO - DEV CONTAINER (SANITIZADA)")
    print("=" * 55)

    # 1. Verificar versión de Python y Sistema Operativo
    print(f" Versión de Python: {sys.version.split()[0]}")
    print(f" Sistema Operativo: {platform.system()} ({platform.release()})")
    print(f" Directorio actual: {os.getcwd()}")

    # 2. Cargar variables de entorno (.env prioritario, .env.example como respaldo)
    raiz_proyecto = Path(__file__).resolve().parent.parent
    ruta_env = raiz_proyecto / ".env"

    if not ruta_env.exists():
        ruta_env = raiz_proyecto / ".env.example"

    if ruta_env.exists():
        load_dotenv(dotenv_path=ruta_env)
        print(f"\n Archivo de configuración cargado: {ruta_env.name}")

        # 3. Comprobar presencia de variables SIN exponer sus valores reales
        variables_requeridas = [
            "OPENAI_API_KEY",
            "MLFLOW_TRACKING_URI",
            "DATABASE_URL",
            "API_BASE_URL",
            "API_KEY",
            "REQUEST_TIMEOUT",
        ]

        print("\n Estado de variables de entorno:")
        for var in variables_requeridas:
            valor = os.getenv(var)
            if valor and valor.strip():
                estado = f"[OK] Configurada ({len(valor)} caracteres)"
            else:
                estado = "[FALTA] No definida o vacía"
            print(f"  - {var:<22}: {estado}")
    else:
        print("\n Error: No se encontró ni .env ni .env.example en la raíz.")

    print("=" * 55)


if __name__ == "__main__":
    verificar_entorno()


