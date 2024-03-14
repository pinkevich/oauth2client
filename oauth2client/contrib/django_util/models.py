# Copyright 2016 Google Inc.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains classes used for the Django ORM storage."""

import base64
import pickle
import jsonpickle

from django.db import models
from django.utils import encoding

from oauth2client.client import Credentials


class CredentialsField(models.Field):
    """Django ORM field for storing OAuth2 Credentials."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('null', True)
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'BinaryField'

    def from_db_value(self, value, expression, connection):
        """Converts the value returned from the database to an instance of this class."""
        return self.to_python(value)

    def to_python(self, value):
        """Converts bytes (from serialization etc) to an instance of this class."""
        if value is None:
            return None
        elif isinstance(value, Credentials):
            return value
        else:
            try:
                return jsonpickle.decode(base64.b64decode(encoding.force_bytes(value)).decode())
            except ValueError:
                return pickle.loads(base64.b64decode(encoding.force_bytes(value)))

    def get_prep_value(self, value):
        """Converts the value from an instance of this class to bytes for the database."""
        if value is None:
            return None
        else:
            return encoding.force_str(base64.b64encode(jsonpickle.encode(value).encode()))

    def value_to_string(self, obj):
        """Converts the field value from the model to a string for serialization."""
        value = getattr(obj, self.attname)
        return self.get_prep_value(value)
