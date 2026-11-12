from datetime import datetime
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from models.news import News
from models.history import History


# 添加浏览记录：用户浏览新闻时记录，同一新闻重复浏览则更新浏览时间并置顶
async def history_add(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    # 查找是否已有浏览记录
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    history = result.scalar_one_or_none()

    if history:
        # 已存在则更新浏览时间，使该记录排到列表最前
        history.created_at = datetime.now()
        await db.commit()
        await db.refresh(history)
        return history

    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


# 删除单条浏览记录
async def remove_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 获取浏览历史列表：获取的是某个用户的浏览历史列表 + 分页功能
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 总量 + 浏览的新闻列表
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 获取浏览历史列表 - 联表查询 join() + 浏览时间排序 + 分页
    # 别名: History.created_at.label("history_time")
    offset = (page - 1) * page_size
    # [
    #   (新闻对象, 浏览时间, 浏览记录id)
    # ]
    query = (select(News, History.created_at.label("history_time"), History.id.label("history_id"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.created_at.desc())
             .offset(offset).limit(page_size)
             )

    result = await db.execute(query)
    rows = result.all()
    return rows, total


# 清空浏览历史
async def remove_all_history(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount or 0