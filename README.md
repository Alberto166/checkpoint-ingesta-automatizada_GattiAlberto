# Checkpoint : Motor de Ingesta Automatizada y Asíncrona

Este repositorio contiene el componente base de ingesta de datos desarrollado bajo principios de **Programación Orientada a Objetos (POO)**, programación asíncrona (`asyncio` + `httpx`) y arquitectura desacoplada, preparado para escalar dentro de un entorno de automatización con IA y MLOps.

## ¿Qué datos descarga el script?

El pipeline consulta de forma concurrente la API pública de [CoinGecko](https://www.coingecko.com/) (`/api/v3/coins/markets`) para obtener métricas de mercado en tiempo real (en USD) de múltiples criptoactivos (`bitcoin`, `ethereum`, `solana`, `cardano`, `ripple`), incluyendo:
- Identificador, símbolo y nombre del activo.
- Precio actual en USD (`current_price_usd`).
- Capitalización de mercado (`market_cap_usd`) y volumen en 24h (`total_volume_24h`).
- Variación porcentual de precio en 24h (`price_change_pct_24h`).
- Marcas de tiempo de actualización de la API y de ingesta en UTC (`ingested_at_utc`).

Los datos limpios se persisten automáticamente en formato `.csv` dentro de la carpeta `data/`.

## Arquitectura del Proyecto

```text
ai-automation-project/
├── config/                 # Configuraciones auxiliares
├── data/                   # Almacenamiento local de datasets generados (.csv)
├── logs/                   # Registros estructurados de ejecución (ingestion.log)
├── src/
│   ├── ingestion/
│   │   ├── client.py       # Clase CryptoAPIClient: comunicación HTTP asíncrona y resiliencia
│   │   └── processor.py    # Clase MarketDataProcessor: parseo y persistencia desacoplados
│   ├── utils/
│   │   └── logger.py       # Configuración centralizada de logging estructurado
│   ├── check_env.py        # Verificación de variables de entorno
│   └── main.py             # Orquestador principal con asyncio.gather()
├── .env.example            # Plantilla de variables de entorno requeridas
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación del proyecto
```

### Decisiones de Diseño y Resiliencia
- **Concurrencia (`asyncio.gather`):** Permite consultar múltiples endpoints en paralelo sin bloquear el hilo de ejecución, reduciendo drásticamente los tiempos de espera de red.
- **Separación de Responsabilidades (POO):** La extracción de datos (`CryptoAPIClient`) está completamente desacoplada de la limpieza, transformación y guardado (`MarketDataProcessor`).
- **Manejo Diferenciado de Errores:**
  - *Errores transitorios* (timeouts, fallos de red, HTTP `429` o `5xx`): Se registran como `WARNING` y aplican reintentos con espera progresiva (*backoff*).
  - *Errores permanentes* (HTTP `400`, `401`, `403`, `404` o recursos inexistentes): Se registran como `ERROR` y se aborta únicamente ese recurso sin interrumpir el resto del pipeline.

## Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <https://github.com/Alberto166/checkpoint-ingesta-automatizada_GattiAlberto>
   cd ai-automation-project
   ```

2. **Crear y activar un entorno virtual (opcional si usás Dev Containers):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Copiá el archivo `.env.example` a `.env` y ajustá los valores si es necesario:
   ```bash
   cp .env.example .env
   ```

### Cambios de Entorno y Dependencias (Módulo 2)
Respecto a la configuración base del Módulo 1, se incorporaron al archivo `requirements.txt` (y al contenedor Docker) las librerías `httpx` (cliente HTTP asíncrono) y `pandas` (estructuración y exportación de datos tabulares).

### Variables de Entorno (`.env.example`)
El proyecto requiere las siguientes variables de configuración:
```env
OPENAI_API_KEY=tu_api_key_aqui
MLFLOW_TRACKING_URI=http://localhost:5000
DATABASE_URL=tu_url_aqui

API_BASE_URL=https://api.coingecko.com/api/v3
API_KEY=opcional_para_coingecko_demo
REQUEST_TIMEOUT=10.0
```

## Ejecución

Desde la carpeta raíz del proyecto, ejecutá el orquestador como módulo de Python:

```bash
python -m src.main
```

Al finalizar, podrás verificar:
- Los registros detallados en consola y en `logs/ingestion.log`.
- El archivo CSV resultante dentro de la carpeta `data/`.

### Ejecutar Tests Automatizados
Para correr la suite de pruebas unitarias (con simulación de respuestas HTTP y timeouts):
```bash
pytest -v
```