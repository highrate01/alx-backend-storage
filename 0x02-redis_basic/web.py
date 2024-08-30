#!/usr/bin/env python3
"""Implementing an expiring web cache and tracker"""
import redis
import requests
from typing import Callable

r = redis.Redis()


def count_access(func: Callable) -> Callable:
    """Decorator to count how many times a URL has been accessed."""
    def wrapper(url: str) -> str:
        key = f"count:{url}"
        r.incr(key)  # Increment access count for the URL
        return func(url)
    return wrapper


def cache_page(func: Callable) -> Callable:
    """Decorator to cache the page result for 10 seconds."""
    def wrapper(url: str) -> str:
        key = f"cached:{url}"
        cached_page = r.get(key)
        if cached_page:
            return cached_page.decode('utf-8')

        # Fetch and cache the page
        page = func(url)
        r.setex(key, 10, page)
        return page
    return wrapper


@count_access
@cache_page
def get_page(url: str) -> str:
    """Fetches the content of a URL."""
    response = requests.get(url)
    return response.text
