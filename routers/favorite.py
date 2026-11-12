from starlette import status
from fastapi import Depends, Query, Request, HTTPException
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite, news

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(default=..., alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(is_favorite=is_favorited))

@router.post("/add")
async def add_favorite(data: FavoriteAddRequest,
                       user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
     result = await favorite.favorite_add(db, user.id, data.news_id)
     return success_response(message="收藏成功", data=result)

@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(default=..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.remove_favorite(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")
    return success_response(message="取消收藏成功")

@router.get("/list")
async def get_favorites(
        page: int = Query(1,ge=1),
        page_size: int = Query(10,ge=1,le=100,alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **{k: v for k, v in news.__dict__.items() if not k.startswith("_")},
        "favorite_time": favorite_time,
        "favorite_id": favorite_id,
    }
    for (news, favorite_time, favorite_id) in rows]
    has_more = total > page_size * page
    data = FavoriteListResponse(list=favorite_list, total=total, has_more=has_more)
    return success_response(message="获取收藏列表成功", data=data)

@router.delete("/clear")
async def clear_favorites(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    count = await favorite.remove_all_favorite(db, user.id)
    return success_response(message=f"清除收藏成功，共清除{count}条收藏")