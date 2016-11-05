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
from .control import AlterControlLockingPanel   # noqa
from .control import AlterControlWSC            # noqa
from .question import AlterQuestionLockingPanel  # noqa
from .question import AlterQuestionWSC           # noqa
import src
from src.db import DBObject, db, NoObjectReturnedFromDB, Course
from src.exceptions import NotDictError, NotStringError, \
    MissingFieldError
from src.utils import standard_name
from src.wsclass import subscribe
from tornado.gen import coroutine
from src.utils import standard_name
import time
class Respuestas(DBObject):
    coll = db.respuestas

class alternativesWSC(src.wsclass.WSClass):
    @subscribe('alternatives.launch', 'w')
    @coroutine
    def launch_alternatives(self, message=None):
        try:
            id_alt = message['question_data']['wording'].replace(' ', '')[0:40]
            id_alt = str(time.time()).split('.')[0]+id_alt
            resp = yield Respuestas.create(id_alt)
            resp.store_dict({'test_name':message['question_data']['test_name']})
            resp.store_dict({'wording':message['question_data']['wording']})
            resp.store_dict({'responses': []})
            resp.store_dict({'answers': message['question_data']['answers']})
            message['question_data']['id_alt'] = id_alt;
            self.pub_subs['d'].send_message(
                    {
                        'type': 'courseMessage({})'.format(self.handler.course.id),
                        'content': {
                            'type': 'alternatives.spread',
                            'content': message
                        }
                    }
                )
            db.courses.update(
                {'_id': self.handler.course.id},
                {'$set':
                    {'onconnect':
                        {
                            'type': 'alternatives.show',
                            'id_alt': message['question_data']['id_alt'],
                            'wording': message['question_data']['wording'],
                            'answers': message['question_data']['answers'],
                            'form': message['question_data']['type']
                        }
                    }
                }
            )
        except:
            raise

    @subscribe('alternatives.spread', 'l')
    def spread_alternatives(self, message=None):
        try:
            self.pub_subs['w'].send_message(
                    {
                        'type': 'alternatives.show',
                        'id_alt': message['content']['question_data']['id_alt'],
                        'wording': message['content']['question_data']['wording'],
                        'answers': message['content']['question_data']['answers'],
                        'form': message['content']['question_data']['type']
                    }
                )
        except:
            raise

    @subscribe('alternatives.close.teacher', 'w')
    def close_alternatives(self, message=None):
        try:
            self.pub_subs['d'].send_message(
                    {
                        'type': 'courseMessage({})'.format(self.handler.course.id),
                        'content': {
                            'type': 'alternatives.close.students',
                            'content': message
                        }
                    }
                )

            db.courses.update(
                {'_id': self.handler.course.id},
                {'$unset':
                    {'onconnect':
                        1
                    }
                }
            )
        except:
            raise

    @subscribe('alternatives.close.students', 'l')
    def close_students_alternatives(self, message=None):
        try:
            self.pub_subs['w'].send_message(
                    {
                            'type': 'alternatives.close.clients',
                    }
                )
        except:
            raise

    @subscribe('alternatives.results.show', 'w')
    def show_alternatives(self, message=None):
        try:
            self.pub_subs['l'].send_message(
                    {
                        'type': 'user.message.frontend.send',
                        'content': {
                            'type': 'alternatives.results.show',
                            'content': message
                        }
                    }
                )
        except:
            raise

    @subscribe('alternatives.results.hide', 'w')
    def hide_alternatives(self, message=None):
        try:
            self.pub_subs['l'].send_message(
                    {
                        'type': 'user.message.frontend.send',
                        'content': {
                            'type': 'alternatives.results.hide',
                            'content': message
                        }
                    }
                )
        except:
            raise

    @subscribe('alternatives.block', 'w')
    def block_alternatives(self, message=None):
        try:
            self.pub_subs['d'].send_message(
                    {
                        'type': 'courseMessage({})'.format(self.handler.course.id),
                        'content': {
                            'type': 'alternatives.block.students',
                            'content': message
                        }
                    }
                )
        except:
            raise

    @subscribe('alternatives.block.students')
    def spread_block_alternatives(self, message=None):
        try:
            self.pub_subs['w'].send_message(
                    {
                            'type': 'alternatives.'+message['content']['action']+'.students'
                    }
                )
        except:
            raise

    @subscribe('alternatives.answer', 'w')
    @coroutine
    def answer_alternatives(self, message=None):
        try:
            answer_list = yield Respuestas.get(message['id_alt'])
            answer_list = answer_list.responses
            for i in answer_list:
                if i['user']== self.handler.user.id:
                    db.respuestas.update(
                        {'_id': message['id_alt']},
                        {'$pull':
                            {'responses':
                                {'alternative': i['alternative'], 'user':self.handler.user.id}
                            }
                        }
                    )

            db.respuestas.update(
                {'_id': message['id_alt']},
                {'$push':
                    {'responses':
                        {'alternative': message['alternative'], 'user':self.handler.user.id}
                    }
                }
            )

            #calcular los porcentajes
            answer_list = yield Respuestas.get(message['id_alt'])
            percentages = dict()
            n_alts = answer_list.answers
            for n in n_alts:
                percentages[n] = 0
            for answer in answer_list.responses:
                alt = answer['alternative']
                if type(alt) == list:
                    for a in alt:
                        percentages[a] +=1
                else:
                    percentages[alt] += 1
            for n in percentages:
                percentages[n] = round((percentages[n]*100.0)/len(answer_list.responses),1)
            results = []
            for i in n_alts: #this should send the dict, but there is no time for this :/
                results.append(percentages[i])

            self.pub_subs['d'].send_message(
                    {
                        'type': self.handler.course_msg_type,
                        'content': {
                            'type': 'teacherMessage',
                            'content': {
                                'type': 'alternatives.update',
                                'content': results #aqui van los porcentajes
                            }
                        }
                    }
                )
        except:
            raise

    @subscribe('alternatives.update', 'l')
    def update_alternatives(self, message=None):
        try:
            self.pub_subs['w'].send_message(
                    {
                            'type': 'alternatives.results',
                            'percentages': message['content']
                    }
                )
        except:
            raise
