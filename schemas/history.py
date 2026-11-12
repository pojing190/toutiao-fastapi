from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
        news_id: int = Field(..., alias="newsId")



# 规划两个类：一个是新闻模型类 + 浏览记录的模型类
class HistoryNewsItemResponse(NewsItemBase):
    history_id: int = Field(alias="historyId")
    history_time: datetime = Field(alias="historyTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 浏览历史列表接口响应模型类
class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )