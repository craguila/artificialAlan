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


class PictureUpload(src.boiler_ui_module.BoilerUIModule):
    id_ = 'picture_upload'
    classes = {'desktop', 'teacher'}
    name = 'Picture Upload'
    conf = {
        'static_url_prefix': '/picture_upload/',
        'static_path': './locking_panels/picture_upload/static',
        'css_files': ['picture_upload.css'],
        'js_files': ['picture_upload.js'],
    }

    def render(self):
        return self.render_string(
            '../locking_panels/picture_upload/picture_upload.html')


class PictureUploadWSC(src.wsclass.WSClass): 
    @subscribe('pic.upload','w')
    def upload_pic(self,message):
        try:
            data = message['data']
            ext = message['name'].split(".")[-1]
            fname = str(uuid.uuid4())
            directory = "static/uploads/"
            bytes_ = b64decode(data)
            file_fullpath = directory+fname+"."+ext
            slidepath = "poweredslides/StaticImg/"+fname+"."+ext
            with open(file_fullpath,"wb") as img:
                img.write(bytes_)
            os.system("convert "+file_fullpath+" -quality 60 " + file_fullpath)
            self.pub_subs['l'].send_message(
                    {
                        'type': 'user.message.frontend.send',
                        'content': {
                            'type': 'pic.upload.ok',
                            'newSlide': {'url':slidepath}
                        }
                    }
                )
        except:
            raise