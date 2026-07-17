# Async Site Checker

Concurrently checks the availability of a list of websites (HTTP
status and response time), using `asyncio` + `aiohttp`. Useful, for
example, for monitoring your own projects or checking a list of job
posting links for dead URLs.

## Installation

```bash
pip install aiohttp
```

## Usage

Create a `sites.txt` file:

```
https://example.com
https://python.org
# this is a comment, will be ignored
https://github.com
```

Run:

```bash
python checker.py sites.txt
python checker.py sites.txt --timeout 5 --concurrency 20
```

## Tests

```bash
pip install aiohttp pytest pytest-asyncio
pytest -v
```

Tests spin up a local test HTTP server via
`aiohttp.test_utils.TestServer` — no real external requests are made
in the tests.

## What this project demonstrates

- `asyncio.gather` + `Semaphore` for controlling concurrency
- Timeouts and network errors are handled and reported separately
- Testing async code against a local test server instead of mocks
- Clean separation of networking / reporting / CLI concerns
