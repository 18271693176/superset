# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from flask import g, Response, request,redirect
from flask_appbuilder.api import expose, safe
from flask_jwt_extended.exceptions import NoAuthorizationError

from superset.views.base_api import BaseSupersetApi
from superset.views.users.schemas import UserResponseSchema
from superset.views.utils import bootstrap_user_data
from flask_login import login_user
import random
import string
import logging

logger = logging.getLogger(__name__)


def generate_random_string(length):
    # 生成候选字符序列，包括所有字母、数字和特殊字符
    characters = string.ascii_letters + string.digits + string.punctuation

    # 使用 random.sample() 从候选字符序列中选择指定长度的字符
    random_string = ''.join(random.sample(characters, length))
    return random_string


# 调用函数生成8位不会重复的随机字符


user_response_schema = UserResponseSchema()


class NopassRestApi(BaseSupersetApi):
    """An api to get information about the current user"""

    resource_name = "nopass"

    @expose("/add", methods=("GET",))
    @safe
    def add(self):
        random_characters = generate_random_string(8)
        username = request.args.get("name")
        role = request.args.get("role", 'Alpha')
        is_admin = request.args.get("isAdmin", None)
        if is_admin == "true":
            role = "Admin"
        user = self.appbuilder.sm.find_user(username=username)
        if user or username.lower() == "admin":
            login_user(user)
            return redirect("/superset/welcome/")
        role_obj = self.appbuilder.sm.find_role(role)
        default_info = {
            "first_name": "first_name",
            "last_name": "last_name",
            "username": username,
            # "active": True,
            "email": f"{random_characters}@superset.com",
            "password": "default",
            # "conf_password": "default"
        }
        try:
            default_info.update({"role": role_obj})
            user = self.appbuilder.sm.add_user(**default_info)
            login_user(user)
        except Exception as e:
            # return self.response(code=500, result={"res": "error", "error": str(e)})
            logger.error(f"login fail. err = {str(e)}")
            return redirect("/superset/welcome/")
        return redirect("/superset/welcome/")
