#!/usr/bin/env python3
"""
exercise.py
"""

import redis
import uuid
from typing import Union, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    a system to count how many times methods of the Cache class are called.
    """
    @wraps(callable)
    def wrapper(self, *argc, **argv):
        key = callable.__qualname__
        self._redis.incr(key)
        return method(self, *argc, **argv)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    to store the history of inputs and outputs for a particular function.
    """
    key = callable.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"

    @wraps(callable)
    def wrapper(self, *args, **kwargs):
        """
        """
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(data))
        return data

    return wrapper


class Cache:
    """
    A Cache class implementation
    """

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        rand_key = str(uuid.uuid4())
        self._redis.set(rand_key, data)
        return rand_key

    def get(self, key: str, fn: Optional[Callable]
            = None) -> Union[str, bytes, int, float]:
        """
        Get data from the cache.

        Args:
            key (str): The key associated with the data.
            fn (Optional[Callable]): A callable function to transform the
            retrieved data.

        Returns:
            Union[str, bytes, int, float]: The retrieved data.
        """
        value = self._redis.get(key)
        if fn and value is not None:
            return fn(value)

        return value

    def get_str(self, key: str) -> str:
        """
        Get a string from the cache.

        Args:
            key (str): The key associated with the string.

        Returns:
            str: The retrieved string.
        """
        value = self._redis.get(key)
        return value.decode('utf-8') if value else ""

    def get_int(self, key: str) -> int:
        """
        Get an integer from the cache.

        Args:
            key (str): The key associated with the integer.

        Returns:
            int: The retrieved integer.
        """
        value = self._redis.get(key)
        try:
            return int(value.decode('utf-8')) if value else 0
        except ValueError:
            return 0


def replay(method: Callable) -> None:
    """
    function to display the history of calls of a particular function.

     Args:
        method (Callable): The function to be replayed.

    Returns:
        None
    """
    name = method.__qualname__
    cache = redis.Redis()
    calls = cache.get(name)
    print(calls)
    if calls:
        calls = calls.decode('utf-8')
        print("{} was called {} times:".format(name, calls))
        inputs = cache.lrange(name + ":inputs", 0, -1)
        outputs = cache.lrange(name + ":outputs", 0, -1)
        for i, o in zip(inputs, outputs):
            print("{}(*{}) -> {}".format(name, i.decode('utf-8'),
                                         o.decode('utf-8')))
    else:
        print("{} has not been called yet.".format(name))
