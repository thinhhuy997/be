from uuid import UUID
from app.utils.exceptions import IdNotFoundException, NameNotFoundException
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import UploadFile, File, Form
from typing import Annotated
import socket
import json
import io
from fastapi_pagination import Params
from app import crud
from app.api import deps
from app.models.proxy_model import Proxy
from app.models.user_model import User
from app.schemas.common_schema import IOrderEnum
from app.schemas.proxy_schema import (
    IProxyCreate,
    IProxyRead,
    IProxyUpdate,
    IproxyIndex,
    IProxyWithCreatedByUser
)
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    IPatchResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum
from app.core.authz import is_authorized

router = APIRouter()


# NEW FILE
def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


@router.post("/multiple-create")
async def create_proxies(
    ip_index: Annotated[int, Form(gt=(-1))], port_index: Annotated[int, Form(gt=(-1))], username_index: Annotated[int, Form(gt=(-1))], password_index: Annotated[int, Form(gt=(-1))],
    # proxy_index: IproxyIndex,
                         file: UploadFile = File(...), 
        current_user: User = Depends(deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])),
        )->IPostResponseBase[list[IProxyWithCreatedByUser]] | IPostResponseBase[None]:
    if not file:
        raise HTTPException(status_code=404, detail="No upload file sent!")
    
    elif file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="File format is invalid!")
    else:
        # String processing...
        all_proxies_str = str(file.file.read())
        all_proxies_str = all_proxies_str[2:-1]
        # separates lines
        all_proxies_str_arr = all_proxies_str.split("\\r\\n")

        proxies = []

        # check valid of the first line and the second line
        if len(all_proxies_str_arr[0]) == 0 and len(all_proxies_str_arr[1]) == 0:
            raise HTTPException(status_code=400, detail="Your file content is incorrect!")
        elif not is_valid_ipv4_address(all_proxies_str_arr[0].split(":")[ip_index]) and \
        not is_valid_ipv4_address(all_proxies_str_arr[1].split(":")[ip_index]):
            raise HTTPException(status_code=400, detail="Your file content is incorrect!")
        else: 
            # Loop through data to convert it to list of json
            for line in all_proxies_str_arr:

                proxy_info = line.split(":")

                ip_item = proxy_info[ip_index]

                # check valid of the the proxy item (valid only if ip is valid)
                if not is_valid_ipv4_address(ip_item):
                    continue
                
                # if valid then ->
                proxy_json = {"ip": proxy_info[ip_index], "port": proxy_info[port_index],
                        "username": proxy_info[username_index], "password": proxy_info[password_index]}
                
                proxies.append(IProxyCreate(**proxy_json))

            # Create multiple proxies
            created_proxies = await crud.proxy.multiple_create(objs_in=proxies, created_by_id=current_user.id)

            return create_response(data=created_proxies)
            
            

@router.get("")
async def get_proxy_list(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProxyRead]:
    """
    Gets a paginated list of heroes
    """
    proxies = await crud.proxy.get_multi_paginated(params=params)
    return create_response(data=proxies)

@router.get("/{proxy_id}")
async def get_proxy_by_id(
    proxy_id: UUID,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IGetResponseBase[IProxyWithCreatedByUser]:
    """
    Gets a track by its id
    """
    proxy = await crud.proxy.get(id=proxy_id)
    if not proxy:
        raise IdNotFoundException(Proxy, proxy_id)
    
    return create_response(data=proxy)

@router.patch("/{proxy_id}")
async def update_proxy(
    proxy_id: UUID,
    proxy: IProxyUpdate,
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    )
) -> IPatchResponseBase[IProxyRead]:
    """
    Updates a proxy by its id

    Required roles:
    - admin
    - manager
    """
    current_proxy = await crud.proxy.get(id=proxy_id)
    if not current_proxy:
        raise IdNotFoundException(Proxy, proxy_id)

    proxy_updated = await crud.hero.update(obj_new=proxy, obj_current=current_proxy)
    return create_response(data=proxy_updated)