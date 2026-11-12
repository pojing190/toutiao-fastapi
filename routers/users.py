from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status
from crud import news
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from schemas.users import (
    UserRequest,
    UserUpdateRequest,
    UserChangePasswordRequest,
    UserAuthResponse,
    UserInfoResponse,
)
from models.users import User
from utils.auth import get_current_user
from utils.response import success_response
from crud import users #导入crud.user里面的两个函数
router = APIRouter(prefix="/api/user", tags=["users"])
@router.post("/register")
async def register_user(user_data: UserRequest,db: AsyncSession = Depends(get_db)):
    #检查用户名是否已存在
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    #创建用户
    new_user = await users.create_user(db, user_data)
    token = await users.create_token(db, new_user.id)


    response_data =  UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(new_user))
    return success_response(message="注册成功",data=response_data)

@router.post("/login")
async def login(user_data: UserRequest,db: AsyncSession = Depends(get_db)):
        user = await users.authenticate_user(db,user_data.username,user_data.password)
        if  not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        token = await users.create_token(db, user.id)
        response_data =  UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
        return success_response(message="登录成功",data=response_data)

@router.get("/info")
async def get_user_info(user:User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))
@router.put("/update")
async def update_user(user_data: UserUpdateRequest,user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
       user = await users.update_user(db, user.username, user_data)
       return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))
@router.put("/password")
async def change_password(password_data: UserChangePasswordRequest,
                          user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
        res_change_password = await users.change_password(db, user, password_data.old_password, password_data.new_password)
        if  not res_change_password:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误")
        return success_response(message="密码更新成功")