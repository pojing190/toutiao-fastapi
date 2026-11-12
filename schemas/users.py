from pydantic import ConfigDict
from pydantic import Field
from typing import Optional
from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    nickname: Optional[str] = Field(None,max_length = 50,description="用户昵称")
    avatar: Optional[str] = Field(None,max_length = 255,description="用户头像")
    gender: Optional[int] = Field(None,max_length = 10,description="用户性别")
    bio: Optional[str] = Field(None,max_length = 500,description="用户个人简介")

class UserInfoResponse(UserInfo):
    id: int
    username: str
    #模型类配置
    model_config = ConfigDict(
        from_attributes = True
    )
#data数据类型

class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(...,alias="user_Info")
    #模型类配置
    model_config = ConfigDict(
        populate_by_name= True,
        from_attributes = True
    )

class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: int = None
    bio: str = None
    phone: str = None

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(...,alias="oldPassword",description="旧密码")
    new_password: str = Field(...,alias="newPassword",description="新密码")