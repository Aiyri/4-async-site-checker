"""
Tests use aiohttp.test_utils to spin up a local test server — no real
external requests are made.

Test dependencies:
    pip install aiohttp pytest pytest-asyncio
"""
import asyncio

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from checker import check_all, load_urls, CheckResult


async def ok_handler(request):
    return web.Response(text="ok", status=200)


async def not_found_handler(request):
    return web.Response(text="nope", status=404)


async def slow_handler(request):
    await asyncio.sleep(2)
    return web.Response(text="slow", status=200)


def make_app():
    app = web.Application()
    app.router.add_get("/ok", ok_handler)
    app.router.add_get("/missing", not_found_handler)
    app.router.add_get("/slow", slow_handler)
    return app


@pytest.mark.asyncio
async def test_check_all_marks_200_as_up():
    server = TestServer(make_app())
    await server.start_server()
    try:
        base = str(server.make_url("/ok"))
        results = await check_all([base], timeout=5, concurrency=5)
        assert results[0].is_up is True
        assert results[0].status == 200
    finally:
        await server.close()


@pytest.mark.asyncio
async def test_check_all_marks_404_as_down():
    server = TestServer(make_app())
    await server.start_server()
    try:
        base = str(server.make_url("/missing"))
        results = await check_all([base], timeout=5, concurrency=5)
        assert results[0].is_up is False
        assert results[0].status == 404
    finally:
        await server.close()


@pytest.mark.asyncio
async def test_check_all_handles_timeout():
    server = TestServer(make_app())
    await server.start_server()
    try:
        base = str(server.make_url("/slow"))
        results = await check_all([base], timeout=1, concurrency=5)
        assert results[0].is_up is False
        assert results[0].error == "timeout"
    finally:
        await server.close()


@pytest.mark.asyncio
async def test_check_all_respects_concurrency_limit():
    """All requests should complete even with concurrency=1 (sequential)."""
    server = TestServer(make_app())
    await server.start_server()
    try:
        base = str(server.make_url("/ok"))
        urls = [base] * 5
        results = await check_all(urls, timeout=5, concurrency=1)
        assert len(results) == 5
        assert all(r.is_up for r in results)
    finally:
        await server.close()


def test_load_urls_skips_comments_and_blank_lines(tmp_path):
    file = tmp_path / "sites.txt"
    file.write_text("https://a.com\n\n# a comment\nhttps://b.com\n")
    urls = load_urls(str(file))
    assert urls == ["https://a.com", "https://b.com"]


def test_check_result_is_up_false_when_error_present():
    result = CheckResult(url="x", status=None, response_time_ms=None, error="timeout")
    assert result.is_up is False


def test_check_result_is_up_true_for_2xx():
    result = CheckResult(url="x", status=200, response_time_ms=15.0)
    assert result.is_up is True
