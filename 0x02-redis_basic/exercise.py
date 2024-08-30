#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Union


class Cache:
    def __init__(self) -> None:
        """initilize the cache with a redis client
        and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stores data in redis using a random key and return the key.
        Args:
            data (Union[Union[str, bytes, int, float]):
                        The data to store in the redis.
        Returns:
            str: The generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)

        return key
