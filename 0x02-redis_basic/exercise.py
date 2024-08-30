#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Union, Optional, Callable


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

    def get(self, key: str,
            fn: Optional[Callable] = None
            ) -> Optional[Union[str, bytes, int, float]]:
        """
        Retrieve data from Redis using the given key and apply conversion func
        Args:
            key (str): The key to retrieve.
            fn: A func to convert the data to desired format.
        Returns:
            Optional[Union[str, bytes, int, float]: The retrieved data.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve the value associated with the key and convert it to str.
        Args:
            key(str): the key to rerieve and convert
        Returns:
            Optional[str]: converted value as a string or none
        """
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve the value associated with the key and convert it to str
        Args:
            key(str): the key to rerieve and convert
        Returns:
            Optional[int]: converted value as a int or none
        """
        return self.get(key, lambda x: int(x))
