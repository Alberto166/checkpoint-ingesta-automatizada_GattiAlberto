import pandas as pd
from src.ingestion.processor import MarketDataProcessor


def test_parse_records_filters_none_and_formats_fields(tmp_path):
    processor = MarketDataProcessor(output_dir=str(tmp_path))

    raw_data = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 60000.5,
            "market_cap": 1200000000,
            "total_volume": 35000000,
            "price_change_percentage_24h": 2.5,
            "last_updated": "2026-11-25T10:00:00Z",
        },
        None,  # Simula un recurso que falló en la descarga
    ]

    clean = processor.parse_records(raw_data)

    assert len(clean) == 1
    assert clean[0]["id"] == "bitcoin"
    assert clean[0]["symbol"] == "BTC"
    assert clean[0]["current_price_usd"] == 60000.5
    assert "ingested_at_utc" in clean[0]


def test_save_to_storage_creates_csv(tmp_path):
    processor = MarketDataProcessor(output_dir=str(tmp_path))
    records = [
        {
            "id": "ethereum",
            "symbol": "ETH",
            "name": "Ethereum",
            "current_price_usd": 3000.0,
            "market_cap_usd": 350000000,
            "total_volume_24h": 15000000,
            "price_change_pct_24h": -1.2,
            "last_updated_api": "2026-11-25T10:00:00Z",
            "ingested_at_utc": "2026-11-25T10:00:05+00:00",
        }
    ]

    csv_path = processor.save_to_storage(records)

    assert csv_path is not None
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert len(df) == 1
    assert df.loc[0, "symbol"] == "ETH"


def test_save_to_storage_empty_list_returns_none(tmp_path):
    processor = MarketDataProcessor(output_dir=str(tmp_path))
    result = processor.save_to_storage([])
    assert result is None
