#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Union, Optional, Callable
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


def call_history(method: Callable) -> Callable:
    """
    decorator to store the history of inputs and outputs for a
    particular function.
    Args:
        method (Callable): Method to be decorated
    Returns:
        Callable: call to store in redis
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wraps method"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)

        self._redis.rpush(output_key, str(result))

        return result
    return wrapper


class Cache:
    def __init__(self) -> None:
        """initilize the cache with a redis client
        and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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

    def get_call_history(self, method: Callable) -> dict:
        """Retrieves the call history of input and output"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        inputs = self._redis.lrange(input_key, 0, -1)
        outputs = self._redis.lrange(output_key, 0, -1)

        return {
                'inputs': inputs,
                'outputs': outputs
                }

def replay(method: Callable):
    """
    Display the history of calls of a particular function.

    Args:
        method (Callable): The method whose history is to be replayed.
    """
    redis_instance = method.__self__._redis

    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    # Fetch the inputs and outputs from Redis
    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")

    for inp, outp in zip(inputs, outputs):
        inp = inp.decode('utf-8')
        outp = outp.decode('utf-8')
        print(f"{method.__qualname__}(*{inp}) -> {outp}")
