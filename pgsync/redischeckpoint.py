"""PGSync RedisCheckpoint."""
import json
import logging
from typing import List, Optional

from redis import Redis
from redis.exceptions import ConnectionError

from .settings import REDIS_READ_CHUNK_SIZE, REDIS_SOCKET_TIMEOUT
from .urls import get_redis_url

logger = logging.getLogger(__name__)


class RedisCheckpoint(object):
    """RedisCheckpoint"""

    def __init__(self, name: str, namespace: str = "checkpoint", **kwargs):
        """Init RedisCheckpoint"""
        url: str = get_redis_url(**kwargs)
        self.key: str = f"{namespace}:{name}"
        try:
            self.__db: Redis = Redis.from_url(
                url,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
            )
            self.__db.ping()
        except ConnectionError as e:
            logger.exception(f"Redis server is not running: {e}")
            raise

    def getCheckpointValue(self) -> int:
        """Get Checkpoint value"""
        checkpoint_value = self.__db.get(self.key)
        try:
            int(checkpoint_value) if checkpoint_value is not None else 0
        except ValueError:
            return 0

    def setCheckpoint(self, checkpoint: int) -> None:
        """Set Checkpoint to Redis"""
        self.__db.set(name=self.key, value=str(checkpoint))

    def deleteCheckpoint(self) -> None:
        """Delete all items from the checkpoint key"""
        logger.info(f"Deleting redis key: {self.key}")
        self.__db.delete(self.key)
