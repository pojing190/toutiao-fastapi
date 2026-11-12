from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category
from sqlalchemy import select
from models.news import News
from sqlalchemy import func
async def  get_categories(db: AsyncSession,skip: int = 0,limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db: AsyncSession,category_id: int,skip: int = 0,limit: int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_count(db: AsyncSession,category_id: int):
    #统计新闻数量当且仅当其id为category_id的，将category_id赋值给News这个类里面的category_id
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_news_detail(db: AsyncSession,news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_news_views(db: AsyncSession,news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    #命中数据行数大于0，说明更新成功
    return result.rowcount > 0

async def get_related_news(db: AsyncSession,news_id: int,category_id: int,limit: int = 5):
     stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),#默认升序，desc为降序
News.publish_time.desc()
        ).limit(limit)
     result = await db.execute(stmt)
    # return result.scalars().all()
    #得到的五条数据是列表
     related_news = result.scalars().all()
    #列表推导式 推导核心数据 然后再return
     return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]