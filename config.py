import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue

# Load environment variables from .env
load_dotenv()

class Config:
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    # Redis Connection
    @staticmethod
    def get_redis_connection():
        return Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
        )

    # RQ Queue
    @staticmethod
    def get_queue():
        redis_conn = Config.get_redis_connection()
        return Queue("default", connection=redis_conn)
