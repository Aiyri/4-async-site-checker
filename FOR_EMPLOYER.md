# Employer-facing description

## Short repo description (GitHub, ~350 chars)

An async site availability checker built with asyncio + aiohttp, using
a semaphore to control concurrency. Distinguishes timeouts from
network errors. Tests run against a local test HTTP server.

## Resume bullet point

- Built an async website monitoring tool using `asyncio` and
  `aiohttp`, with concurrency controlled via a `Semaphore` to keep
  load on checked resources predictable
- Wrote tests for async code using a local test server
  (`aiohttp.test_utils.TestServer`) instead of mocks — tests verify
  real network behavior (timeouts, status codes) with no external
  dependencies

## What to say in an interview

- Key point: why `asyncio.Semaphore` instead of a plain
  `asyncio.gather` with no limits — without concurrency control,
  checking hundreds of sites can hit OS limits on open connections or
  get you rate-limited by the servers you're checking
- A timeout and a network error are different states
  (`asyncio.TimeoutError` vs `aiohttp.ClientError`), and the report
  distinguishes them on purpose — for a monitoring tool, knowing
  whether a site is slow or actually down matters
- If asked "why not requests" — explain sync vs async I/O: for
  checking N sites concurrently, asyncio significantly outperforms
  threading or sequential requests
