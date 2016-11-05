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


class LaserPointer(src.boiler_ui_module.BoilerUIModule):
    id_ = 'laser-pointer'
    classes = {'desktop', 'teacher'}
    name = 'Laser Pointer'
    conf = {
        'static_url_prefix': '/laser_pointer/',
        'static_path': './locking_panels/laser_pointer/static',
        'css_files': ['laser_pointer.css'],
        'js_files': ['laser_pointer.js'],
    }

    def render(self):
        return self.render_string(
            '../locking_panels/laser_pointer/laser_pointer.html')


class LaserPointerWSC(src.wsclass.WSClass): 
    @subscribe('laser.hide', 'w')
    def laser_hide(self, message=None):
        try:
            self.pub_subs['l'].send_message(
                    {
                        'type': 'user.message.frontend.send',
                        'content': {
                            'type': 'laser.hide'
                        }
                    }
                )
        except:
            raise
    
    @subscribe('laser.move', 'w')
    def laser_move(self, message=None):
        try:
            self.pub_subs['l'].send_message(
                    {
                        'type': 'user.message.frontend.send',
                        'content': {
                            'type': 'laser.move',
                            'x':message['x'],
                            'y':message['y']
                        }
                    }
                )
        except:
            raise
                        