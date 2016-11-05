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


class SlidesPanel(src.boiler_ui_module.BoilerUIModule):
    id_ = 'slides-panel'
    classes = {'desktop', 'scrolling-panel', 'teacher'}
    name = 'Diapositivas'
    conf = {
        'static_url_prefix': '/slides/',
        'static_path': './panels/slides/static',
        'css_files': ['slides.css'],
        'js_files': ['slides.js'],
    }

    def render(self):
        return self.render_string(
            '../panels/slides/slides.html')


class Slide(DBObject):
    coll = db.slides

    @classmethod  # noqa
    @coroutine
    def create(cls, user, data):
        """Create a new slideshow document in the database.

        :param src.bd.User user:
            The user that will own the slideshow.

        :param dict data:
            The data that should be used to create the new
            slideshow object.

            ``data`` should have the following format:

            .. code-block:: python

                {
                    'name': 'Slideshow Name',
                    'slides': [
                        {
                            'url': 'my.slides.com#slide1',
                            'question': {
                                'type': 'alternatives',
                                'wording': 'A question?',
                                'answers': [
                                    'Answer 1.',
                                    'Answer 2.',
                                    ...
                                ]
                            }
                        },
                        ...
                    ]
                }

            Where ``'Slideshow Name'`` should be the name of
            the slideshow, ``'my.slides.com#slide1'`` can be
            any valid URL, ``'A question?'`` should be an
            associated question to be asked using this slide
            and ``'Answer #.'`` are the different answer
            alternatives for the question.

            Currently the only supported question type is
            ``'alternatives'``.

            A presentation can have any number of slides and
            a question can have any number of answers.

            The object associated to the key ``'question'``
            can be ``None`` (``'question': None``).

        :return:
            A new slideshow object.
        :rtype: :class:`Slide`

        :raises AttributeError:
            If ``user`` has no attribute ``id``.

        :raises NotDictError:
            If ``data`` is not a dictionary.

        :raises NotStringError:
            If ``user.id`` or ``data['name']`` is not a
            string.

        :raises KeyError:
            If ``data`` has no key ``name``.

        :raises pymongo.errors.OperationFailure:
            If an database error occurred during creation.

        :raises pymongo.errors.DuplicateKeyError:
            If an object with the same id alredy exists in
            the database.
            :class:`~pymongo.errors.DuplicateKeyError` is a
            subclass of
            :class:`~pymongo.errors.OperationFailure`.

        :raises ConditionNotMetError:
            If the just created slide document no longer
            exists in the database. This should never
            happen!
        """
        try:
            id_ = user.id + standard_name(data['name'])
            self = yield super().create(id_)
            data['user_id'] = user.id
            yield self.store_dict(data)
            return self

        except AttributeError as e:
            if not hasattr(user, 'id'):
                ae = AttributeError(
                    "'user' has no attribute 'id'")
                raise ae from e

            else:
                raise

        except TypeError as te:
            if not isinstance(data, dict):
                raise NotDictError('data') from te

            elif not isinstance(data['name'], str):
                raise NotStringError("data['name']") from te

            elif not isinstance(user.id, str):
                raise NotStringError('user.id') from te

            else:
                raise

        except KeyError as e:
            if 'name' not in data:
                ke = KeyError("'data' has no key 'name'")
                raise ke from e

            else:
                raise

        except:
            raise

    @classmethod
    @coroutine
    def get_user_slide_list(cls, user):
        """
        .. todo::
            *   Review the error handling and documentation
                of this funcion.
        """
        try:
            yield db.users.ensure_index('user_id')
            slides = yield cls.get_list(
                {'user_id': user.id},
                ['_id', 'name']
            )
            return slides

        except:
            raise

def pdf_to_html_json(presentation_fullpath, dest_dir=None, conv_to_img=1, url='https://lucas.tidys.io/', original_name=''):

    # Get directory, filename, extension
    name_length = len(presentation_fullpath.split('/')[-1])
    directory = presentation_fullpath[0:-1*name_length]     # includes '/'
    filename = presentation_fullpath.split('/')[-1].split('.')[0]
    extension = presentation_fullpath.split('.')[-1]


    try:
        # Check if file exists
        if not os.path.isfile(presentation_fullpath):
            raise Exception("Error: File doesn't exist")

        # If file is a ppt, convert to pdf
        elif extension in ['ppt', 'pptx', 'odp']:
            command =   'libreoffice --headless --invisible --convert-to pdf ' + \
                        presentation_fullpath + ' --outdir ' + directory
            call(command.split(' '))

        # If not a ppt or pdf, return
        elif extension != 'pdf':
            raise Exception("Error: Invalid file type")

    except Exception as e:
        print(e.args[0])
        return


    # Get filenames
    pdf_filename = filename + '.pdf'
    html_filename = filename + '.html'
    json_filename = filename + '.json'

    # Create output directory
    temp_dir = directory + filename + '/'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Copy style.css
    copyfile('panels/slides/ppt_parser.css', temp_dir + 'style.css')


    # Convert pdf to image and write html manually
    if conv_to_img:
        # Using Imagemagick
        # command = 'convert -density 432 ' + directory + pdf_filename + ' -quality 100 ' + temp_dir + filename + '.png'

        # Using pdf2svg
        command = 'pdf2svg ' + directory + pdf_filename + ' ' + temp_dir + filename + '-%d.svg all'

        call(command.split(' '))

        html = open(temp_dir + html_filename, 'w')

        # Count number of png images, which is the number of pages in the pdf
        png_counter = 0
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.svg'):
                    png_counter += 1

        # Write html
        html.write('<!DOCTYPE html>\n')
        html.write('<html>\n')
        html.write('<head>\n')
        html.write('    <meta charset="utf-8">\n')
        html.write('    <meta name="generator" content="pandoc">\n')
        html.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">\n')
        html.write('    <title></title>\n')
        html.write('    <style type="text/css">code{white-space: pre;}</style>\n')
        html.write('    <link rel="stylesheet" href="style.css">\n')
        html.write('    <!--[if lt IE 9]>\n')
        html.write('    <script src="//cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.3/html5shiv-printshiv.min.js"></script>\n')
        html.write('    <![endif]--><link rel="stylesheet" href="https://use.fontawesome.com/4b0be90c69.css" media="all">\n')
        html.write('</head>\n')
        html.write('<body>\n')

        for i in range(png_counter):
            html.write('    <section id="pf' + format(i + 1,'0x') + '" class="level1 vflex">')
            html.write('        <figure>\n')
            html.write('            <img src="' + filename + '-' + str(i + 1) + '.svg" />\n')
            html.write('        </figure>\n')
            html.write('    </section>\n')

        html.write('</body>\n')
        html.write('</html>\n')

        html.close()


    else:
        # Command to generate html using pdf2htmlex dockerfile
        command =   'docker run -ti --rm -v ' + directory + \
                    ':/pdf bwits/pdf2htmlex pdf2htmlEX --embed cfijo ' + \
                     '--dest-dir ' + filename + ' --zoom 1.3 ' + pdf_filename

        call(command.split(' '))



    # Read html document and get the Ids of every page
    page = []

    html = open(temp_dir + html_filename, 'r')

    for line in html.readlines():
        if line.startswith('<div id="pf') or '<section id="pf' in line:
            page.append(line.split('"')[1])

    html.close()


    html_url = url + filename + '/' + html_filename

    # Create json file as dictionary, then dump into file
    json_dict = {}
    if original_name == '':
        original_name = filename
    json_dict["name"] = original_name[:-1*original_name[::-1].find('.')-1]
    json_dict["slides"] = []

    for item in page:
        temp = {}
        temp["url"] = html_url + '#' + item
        json_dict["slides"].append(temp)
        del temp

    with open(temp_dir + json_filename, 'w') as fp:
        json.dump(json_dict, fp)

    return json_dict



class SlidesWSC(src.wsclass.WSClass):
    class parses(object):
        parser_names = {}

        def __init__(self, mime_type):
            self.mime_type = mime_type

        def __call__(self, meth):
            self.parser_names[self.mime_type] = \
                meth.__name__
            return meth

    def __init__(self, handler):
        super().__init__(handler)

        self.parsers = {
            mime_type: getattr(self, meth_name)
            for mime_type, meth_name in
            self.parses.parser_names.items()
        }

    @subscribe('slides.get')
    @coroutine
    def send_slide_data(self, message):
        try:
            data = yield Slide.get_one_document(
                message['_id'])

        except TypeError:
            if not isinstance(message, dict):
                self.handler.send_malformed_message_error(
                    message)
            else:
                raise

        except KeyError:
            if '_id' not in message:
                self.handler.send_malformed_message_error(
                    message)
            else:
                raise

        except NoObjectReturnedFromDB:
            self.handler.send_malformed_message_error(
                message)
        except:
            raise

        else:
            self.pub_subs['d'].send_message(
                    {
                        'type': 'courseMessage({})'.format(self.handler.course.id),
                        'content': {
                            'type': 'slides.spread',
                            'content': {
                                'type': 'slides.get.ok',
                                'slide': data
                            }
                        }
                    }
                )
            #self.pub_subs['w'].send_message(
            #    {'type': 'slides.get.ok', 'slide': data})

    @subscribe('slides.spread')
    def spread_slides(self, message=None):
        self.pub_subs['w'].send_message(
            message['content'])

    @subscribe('slides.list.get')
    @coroutine
    def send_slide_list(self, message=None):
        """
        .. todo::
            *   Review the error handling and documentation
                of this funcion.
        """
        try:
            slides = yield Slide.get_user_slide_list(
                self.handler.user)

        except:
            raise

        else:
            self.pub_subs['w'].send_message(
                {
                    'type': 'slides.list.get.ok',
                    'slides': slides
                }
            )

    @subscribe('slides.add')
    @coroutine
    def add_slides(self, message):
        """
        .. todo::
            *   Review the error handling and documentation
                of this funcion.
        """
        try:
            mime_type = message['mime']
            data = self.parsers[mime_type](message['data'],message['name'] )
            slide = yield Slide.create(
                self.handler.user, data)

        except Exception as e:
            raise
            self.pub_subs['w'].send_message(
                {
                    'type': 'slides.add.error',
                    'cause': str(e),
                    'message':
                        'Ocurrió una excepción dutante la '
                        'creación de la nueva presentación.'
                }
            )

        else:
            self.pub_subs['w'].send_message(
                {
                    'type': 'slides.add.ok',
                    '_id': slide.id,
                    'name': slide.name,
                }
            )

    def change_slide(self, previous=False):
        """
        .. todo::
            *   Review the error handling and documentation
                of this funcion.
        """
        try:
            instruction = 'prev' if previous else 'next'
            msg_type = 'slides.{}'.format(instruction)

            self.pub_subs['l'].send_message(
                {
                    'type': 'user.message.frontend.send',
                    'content': {
                        'type': msg_type
                    }
                }
            )
        except:
            raise

    @subscribe('slides.prev', 'w')
    def show_prev_slide(self, message=None):
        """
        .. todo::
            *   Review the error handling and documentation
                of this funcion.
        """
        try:
            self.change_slide(previous=True)
        except:
            raise

    @subscribe('slides.next', 'w')
    def show_next_slide(self, message=None):
        """
        .. todo::
            *   Review the error handling and documentation
                of this funcion.
        """
        try:
            self.change_slide()
        except:
            raise




    @parses('application/json')
    def json_parser(self, data, name):
        try:
            bytes_ = b64decode(data)
            json_ = bytes_.decode()
            data = json.loads(json_)

            if 'name' not in data:
                raise MissingFieldError('data', 'name')

            elif 'slides' not in data:
                raise MissingFieldError('data', 'slides')

            elif not isinstance(data['name'], str):
                raise NotStringError("data['name']")

            elif not isinstance(data['slides'], list):
                raise TypeError(
                    "data['slides'] should be a list.")

            elif len(data['slides']) < 1:
                raise ValueError(
                    "data['slides'] should have at least "
                    "one slide.")

            elif not all(
                    'url' in s for s in data['slides']):
                raise MissingFieldError('All slides', 'url')

            else:
                return data

        except:
            raise





    @parses('application/pdf')
    def pdf_parser(self, data, name):
        try:
            fname = str(uuid.uuid4())
            directory = "static/uploads/"+fname
            bytes_ = b64decode(data)
            presentation_fullpath = directory+"/"+fname+".pdf"

            os.system("mkdir "+directory)
            with open(directory+"/"+fname+".pdf","wb") as pdf:
                pdf.write(bytes_)

            json_dict = pdf_to_html_json(presentation_fullpath, directory, 1, directory+"/", name)
            return json_dict

        except:
            raise

    @parses('application/vnd.ms-powerpoint')
    def ppt_parser(self, data, name):
        try:
            fname = str(uuid.uuid4())
            directory = "static/uploads/"+fname
            bytes_ = b64decode(data)
            presentation_fullpath = directory+"/"+fname+".ppt"

            os.system("mkdir "+directory)
            with open(directory+"/"+fname+".ppt","wb") as ppt:
                ppt.write(bytes_)

            json_dict = pdf_to_html_json(presentation_fullpath, directory, 1, directory+"/", name)
            return json_dict

        except:
            raise

    @parses('application/vnd.openxmlformats-officedocument.presentationml.presentation')
    def ppt_parser(self, data, name):
        try:
            fname = str(uuid.uuid4())
            directory = "static/uploads/"+fname
            bytes_ = b64decode(data)
            presentation_fullpath = directory+"/"+fname+".pptx"

            os.system("mkdir "+directory)
            with open(directory+"/"+fname+".pptx","wb") as pptx:
                pptx.write(bytes_)

            json_dict = pdf_to_html_json(presentation_fullpath, directory, 1, directory+"/", name)
            return json_dict

        except:
            raise

    parses('attachment/json')(json_parser)
    parses('')(json_parser)
