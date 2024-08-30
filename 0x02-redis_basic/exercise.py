#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Union, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    A decorator that count how many times a method is called
    Args:
        method (Callable): Method to be decorated.
    Returns:
        Callable: call counts in redis
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wraps method"""
        key = method.__qualname__
        self._redis.incr(key)

        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    def __init__(self) -> None:
        """initilize the cache with a redis client
        and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
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
            fn: Callable = None
            ) -> Union[str, bytes, int, float, None]:
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

    def get_str(self, key: str) -> Union[str, None]:
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
