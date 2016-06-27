from StringIO import StringIO
import os
import errno

import PIL.Image

from .models import Image
from . import db


def make_path(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise


def upload_image(file_object):
    dbimage = Image()
    db.session.add(dbimage)
    db.session.commit()
    directory = dbimage.directory
    filename = dbimage.filename
    path = os.path.join(directory, filename)
    make_path(directory)
    img = PIL.Image.open(StringIO(file_object))
    img.save(path, format=img.format)
    dbimage.file_extension = img.format
    db.session.add(dbimage)
    db.session.commit()
    return dbimage
