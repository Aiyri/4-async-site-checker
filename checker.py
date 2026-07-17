"""
Async Site Checker
Checks the availability of a list of sites concurrently and reports
response time.

Usage:
    python checker.py sites.txt
    python checker.py sites.txt --timeout 5 --concurrency 20

sites.txt format: one URL per line.
"""
import argparse
import asyncio
import time
from dataclasses import dataclass

import aiohttp


@dataclass
class CheckResult:
    url: str
    status: int | None
    response_time_ms: float | None
    error: str | None = None

    @property
    def is_up(self) -> bool:
        return self.error is None and self.status is not None and self.status < 400


async def check_site(
    session: aiohttp.ClientSession,
    url: str,
    timeout: int,
    semaphore: asyncio.Semaphore,
) -> CheckResult:
    """Checks a single site, limiting concurrency via a semaphore."""
    async with semaphore:
        start = time.monotonic()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                elapsed_ms = (time.monotonic() - start) * 1000
                return CheckResult(url=url, status=response.status, response_time_ms=round(elapsed_ms, 1))
        except asyncio.TimeoutError:
            return CheckResult(url=url, status=None, response_time_ms=None, error="timeout")
        except aiohttp.ClientError as exc:
            return CheckResult(url=url, status=None, response_time_ms=None, error=str(exc))


async def check_all(urls: list[str], timeout: int = 10, concurrency: int = 10) -> list[CheckResult]:
    """Checks a list of URLs concurrently, with at most `concurrency` in flight at once."""
    semaphore = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        tasks = [check_site(session, url, timeout, semaphore) for url in urls]
        return await asyncio.gather(*tasks)


def load_urls(file_path: str) -> list[str]:
    """Reads a list of URLs from a file, skipping blank lines and comments."""
    urls = []
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def print_report(results: list[CheckResult]) -> None:
    """Prints a report: down sites first, then up sites sorted by response time."""
    down = [r for r in results if not r.is_up]
    up = sorted([r for r in results if r.is_up], key=lambda r: r.response_time_ms)

    if down:
        print("DOWN:")
        for r in down:
            reason = r.error or f"HTTP {r.status}"
            print(f"  {r.url} — {reason}")
        print()

    if up:
        print("UP:")
        for r in up:
            print(f"  {r.url} — {r.status}, {r.response_time_ms} ms")

    print(f"\nTotal: {len(up)}/{len(results)} up")


def main():
    parser = argparse.ArgumentParser(description="Site availability checker")
    parser.add_argument("file", help="File with a list of URLs (one per line)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent requests")
    args = parser.parse_args()

    urls = load_urls(args.file)
    if not urls:
        print("URL list is empty.")
        return

    results = asyncio.run(check_all(urls, args.timeout, args.concurrency))
    print_report(results)


if __name__ == "__main__":
    main()
