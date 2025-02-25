#!/usr/bin/env python3
"""
exercise.py
"""

import redis
import uuid
from typing import Union, Optional, Callable


class Cache:
    """
    A Cache class implementation
    """

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

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
