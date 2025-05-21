# POC Rate Limiter

This is a simple POC for a Rate Limiter in Python using Asyncio (with Lock) + internal in-memory dict for storing requests.

Internally, I'm storing the timestamp in seconds for each request, while checking if the current request is allowed within a specific time window in seconds.

There are a few test cases trying to force a race condition, running multiple requests and clients.
