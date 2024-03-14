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
from django.utils.encoding import force_bytes, force_str

from oauth2client.client import Credentials


class CredentialsField(models.Field):
    """Django ORM field for storing OAuth2 Credentials."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('null', True)
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'BinaryField'

    def from_db_value(self, value, expression, connection):
        """Overrides ``models.Field`` method. This converts the value
        returned from the database to an instance of this class.
        """
        return self.to_python(value)

    def to_python(self, value):
        """Overrides ``models.Field`` method. This is used to convert
        bytes (from serialization etc) to an instance of this class"""
        if value is None:
            return None
        elif isinstance(value, Credentials):
            return value
        else:
            try:
                decoded = force_str(base64.b64decode(force_bytes(value)))
                return jsonpickle.decode(decoded)
            except UnicodeDecodeError:
                try:
                    return pickle.loads(base64.b64decode(force_bytes(value)))
                except (pickle.PickleError, EOFError) as e:
                    raise ValueError(f"Error decoding with pickle: {e}")
            except ValueError as e:
                raise ValueError(f"Error decoding value: {e}")

    def get_prep_value(self, value):
        """Overrides ``models.Field`` method. This is used to convert
        the value from an instances of this class to bytes that can be
        inserted into the database.
        """
        if value is None:
            return None
        else:
            encoded = base64.b64encode(jsonpickle.encode(value, unpicklable=False).encode())
            return force_bytes(encoded)

    def value_to_string(self, obj):
        """Convert the field value from the provided model to a string.

        Used during model serialization.

        Args:
            obj: db.Model, model object

        Returns:
            string, the serialized field value
        """
        value = self.value_from_object(obj)
        prep_value = self.get_prep_value(value)
        return force_str(prep_value)
