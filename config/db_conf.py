import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine

load_dotenv()

#数据库url（从环境变量读取，敏感信息不写入代码）
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "news_app")

ASYNC_DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

   #创建异步会话工厂
async_session = async_sessionmaker(
    bind = async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

   #创建依赖项
async def get_db():
    async with async_session() as session:
        try:
           yield session
           await session.commit()
        except Exception :
           await session.rollback()
           raise
        finally:
            await session.close()