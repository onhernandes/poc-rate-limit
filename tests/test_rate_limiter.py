import pytest
import asyncio
from src.rate_limiter import RateLimiter


@pytest.fixture
def rate_limiter():
    return RateLimiter(max_requests=5, time_window=60)


@pytest.mark.asyncio
async def test_basic_rate_limiting():
    client_id = "test_client"
    rate_limiter = RateLimiter(max_requests=4, time_window=2)

    for i in range(4):
        assert await rate_limiter.is_allowed(client_id) is True
        await asyncio.sleep(0.4)

    assert await rate_limiter.is_allowed(client_id) is False

    await asyncio.sleep(1)

    assert await rate_limiter.is_allowed(client_id) is True


@pytest.mark.asyncio
async def test_concurrent_requests(rate_limiter: RateLimiter):
    client_id = "test_client"

    async def make_request():
        return await rate_limiter.is_allowed(client_id)

    tasks = [make_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)

    assert sum(results) == 5


@pytest.mark.asyncio
async def test_multiple_clients():
    client_ids = [f"client_{i}" for i in range(5)]
    rate_limiter = RateLimiter(max_requests=5, time_window=1)

    async def make_parallel_requests(client_id):
        async def single_request():
            return await rate_limiter.is_allowed(client_id)

        tasks = [single_request() for _ in range(10)]
        return await asyncio.gather(*tasks)

    all_results = await asyncio.gather(
        *[make_parallel_requests(client_id) for client_id in client_ids]
    )

    for client_results in all_results:
        assert sum(client_results) == 5


@pytest.mark.asyncio
async def test_race_condition_simulation(rate_limiter):
    client_id = "test_client"

    async def delayed_request(delay):
        await asyncio.sleep(delay)
        return await rate_limiter.is_allowed(client_id)

    delays = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    tasks = [delayed_request(delay) for delay in delays]
    results = await asyncio.gather(*tasks)

    assert sum(results) == 5


@pytest.mark.asyncio
async def test_multiple_clients_race_condition():
    client_ids = [f"client_{i}" for i in range(5)]
    rate_limiter = RateLimiter(max_requests=5, time_window=1)

    async def make_delayed_requests(client_id):
        async def delayed_request(delay):
            await asyncio.sleep(delay)
            return await rate_limiter.is_allowed(client_id)

        delays = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
        tasks = [delayed_request(delay) for delay in delays]
        return await asyncio.gather(*tasks)

    all_results = await asyncio.gather(
        *[make_delayed_requests(client_id) for client_id in client_ids]
    )

    for client_results in all_results:
        assert sum(client_results) == 5


@pytest.mark.asyncio
async def test_rapid_succession_requests(rate_limiter):
    client_id = "test_client"

    async def rapid_request():
        return await rate_limiter.is_allowed(client_id)

    tasks = []
    for _ in range(10):
        tasks.append(rapid_request())
        await asyncio.sleep(0.001)

    results = await asyncio.gather(*tasks)
    assert sum(results) == 5


@pytest.mark.asyncio
async def test_stress_test(rate_limiter):
    client_id = "test_client"

    async def stress_request():
        return await rate_limiter.is_allowed(client_id)

    num_requests = 10000
    tasks = [stress_request() for _ in range(num_requests)]
    results = await asyncio.gather(*tasks)

    assert sum(results) == 5
