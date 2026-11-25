import httpx
import pytest
from src.ingestion.client import CryptoAPIClient


@pytest.mark.asyncio
async def test_fetch_coin_market_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 65000}],
        )

    async with CryptoAPIClient(base_url="https://test.com", max_retries=2) as client:
        client._client = httpx.AsyncClient(
            base_url="https://test.com", transport=httpx.MockTransport(handler)
        )
        result = await client.fetch_coin_market("bitcoin")

    assert result is not None
    assert result["id"] == "bitcoin"
    assert result["current_price"] == 65000


@pytest.mark.asyncio
async def test_fetch_coin_market_timeout_retries_and_returns_none(monkeypatch):
    async def fast_sleep(_):
        pass

    monkeypatch.setattr("asyncio.sleep", fast_sleep)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("Simulated timeout")

    async with CryptoAPIClient(base_url="https://test.com", max_retries=3) as client:
        client._client = httpx.AsyncClient(
            base_url="https://test.com", transport=httpx.MockTransport(handler)
        )
        result = await client.fetch_coin_market("bitcoin")

    assert result is None
    assert attempts == 3


@pytest.mark.asyncio
async def test_fetch_coin_market_429_transient_recovers(monkeypatch):
    async def fast_sleep(_):
        pass

    monkeypatch.setattr("asyncio.sleep", fast_sleep)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, text="Rate limit exceeded")
        return httpx.Response(200, json=[{"id": "solana", "symbol": "sol", "current_price": 150}])

    async with CryptoAPIClient(base_url="https://test.com", max_retries=3) as client:
        client._client = httpx.AsyncClient(
            base_url="https://test.com", transport=httpx.MockTransport(handler)
        )
        result = await client.fetch_coin_market("solana")

    assert result is not None
    assert result["id"] == "solana"
    assert attempts == 2


@pytest.mark.asyncio
async def test_fetch_coin_market_404_permanent_aborts_immediately():
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(404, text="Not Found")

    async with CryptoAPIClient(base_url="https://test.com", max_retries=3) as client:
        client._client = httpx.AsyncClient(
            base_url="https://test.com", transport=httpx.MockTransport(handler)
        )
        result = await client.fetch_coin_market("fake-coin")

    assert result is None
    assert attempts == 1  # No reintenta ante errores permanentes 4xx
