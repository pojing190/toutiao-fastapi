from starlette import status
from fastapi import Depends, Query, Request, HTTPException
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import history

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
async def add_history(data: HistoryAddRequest,
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    result = await history.history_add(db, user.id, data.news_id)
    return success_response(message="添加浏览记录成功", data=result)

@router.delete("/delete/{news_id}")
async def remove_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.remove_history(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="浏览记录不存在")
    return success_response(message="删除浏览记录成功")

@router.get("/list")
async def get_history(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [{
        **{k: v for k, v in news.__dict__.items() if not k.startswith("_")},
        "history_time": history_time,
        "history_id": history_id,
    }
    for (news, history_time, history_id) in rows]
    has_more = total > page_size * page
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取浏览历史列表成功", data=data)

@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    count = await history.remove_all_history(db, user.id)
    return success_response(message=f"清除浏览历史成功，共清除{count}条记录")