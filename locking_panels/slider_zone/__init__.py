# -*- coding: UTF-8 -*-

import json
from base64 import b64decode

from tornado.gen import coroutine

import os
import uuid
import src
from src.db import DBObject, db, NoObjectReturnedFromDB
from src.exceptions import NotDictError, NotStringError, \
    MissingFieldError
from src.utils import standard_name
from src.wsclass import subscribe

from subprocess import call
from shutil import move, copyfile, rmtree
import json


class SliderZone(src.boiler_ui_module.BoilerUIModule):
    id_ = 'slider_zone'
    classes = {'desktop', 'teacher'}
    name = 'SliderZone'
    conf = {
        'static_url_prefix': '/slider_zone/',
        'static_path': './locking_panels/slider_zone/static',
        'css_files': ['slider_zone.css'],
        'js_files': ['slider_zone.js'],
    }

    def render(self):
        return self.render_string(
            '../locking_panels/slider_zone/slider_zone.html')


class TimerWSC(src.wsclass.WSClass): 
    pass