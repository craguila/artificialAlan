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


class Timer(src.boiler_ui_module.BoilerUIModule):
    id_ = 'timer'
    classes = {'desktop', 'teacher'}
    name = 'Timer'
    conf = {
        'static_url_prefix': '/timer/',
        'static_path': './locking_panels/timer/static',
        'css_files': ['timer.css'],
        'js_files': ['timer.js'],
    }

    def render(self):
        return self.render_string(
            '../locking_panels/timer/timer.html')


class TimerWSC(src.wsclass.WSClass): 
    @subscribe('timer.start', 'w')
    def start_timer(self, message=None):
        try:
            self.pub_subs['l'].send_message(
                    {
                        'type': 'user.message.frontend.send',
                        'content': {
                            'type': 'timer.start',
                            'time': message['time']
                        }
                    }
                )
        except:
            raise