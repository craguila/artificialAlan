# -*- coding: UTF-8 -*-

# COPYRIGHT (c) 2016 Cristóbal Águila
#
# GNU AFFERO GENERAL PUBLIC LICENSE
#    Version 3, 19 November 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import src
from src.db import DBObject, db, NoObjectReturnedFromDB
from src.exceptions import NotDictError, NotStringError, \
    MissingFieldError
from src.utils import standard_name
from src.wsclass import subscribe
from tornado.gen import coroutine
from src.utils import standard_name
import time


class StaticImg(src.boiler_ui_module.BoilerUIModule):
    id_ = 'StaticImg'
    conf = {
        'static_url_prefix': '/StaticImg/',
        'static_path': './poweredslides/StaticImg/static',
        'css_files': ['StaticImg.css'],
        'js_files': [],
    }
    
    @coroutine
    def fetch_data(cls,pid):
      return "/static/uploads/"+pid

    def render(self,title, data):
        return self.render_string('../poweredslides/StaticImg/StaticImg.html',src=data)