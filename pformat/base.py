'''How to override string formatters:

Source: https://github.com/python/cpython/blob/9bbcbc9f6dfe1368fe7330b117707f828e6a2c18/Lib/string.py#L159

The call sequence for `Formatter.format` is as follows:
 - format(self, format_string, /, *args, **kwargs)
     - vformat(self, format_string, args, kwargs)
         - _vformat(self, format_string, args, kwargs, used_args, recursion_depth,
                    auto_arg_index=0)

            # get the object for field_name from args and kwargs
            # field_name is either a list index or a dict key -
            - obj, arg_used = self.get_field(field_name, args, kwargs)

            # do type conversion on the given object
            - obj = self.convert_field(obj, conversion)

            # recursively fill format string with format vars
            - format_spec, auto_arg_index = self._vformat(
                    format_spec, args, kwargs,
                    used_args, recursion_depth-1,
                    auto_arg_index=auto_arg_index)

            #
            - self.format_field(obj, format_spec)

        - check_unused_args(used_args, args, kwargs)


What we're doing is hooking into `get_field`, `convert_field`, and `format_field` using
a custom class `Field` that we use to collect all of the field format info and signify
that we want to perform a modification on (i.e. `if isinstance(obj, Field)`).


'''

import string

class _NoValueMeta(type):
    def __repr__(cls):
        return '<No Value>'

    def __str__(cls):
        return '--'

    def __nonzero__(cls):
        return False

class _NoValue:
    __metaclass__ = _NoValueMeta


class Formatter(string.Formatter):
    MISSING_KEY_EXCEPTION = (KeyError, IndexError, AttributeError)

    '''

    Original methods

    '''

    def get_field(self, key, a, kw):
        try:
            return super().get_field(key, a, kw)
        except self.MISSING_KEY_EXCEPTION as e:
            return self.missing_field(e, key, a, kw)

    def convert_field(self, obj, conversion):
        if is_field(obj):
            obj.conv = conversion
            return self.convert_field_obj(obj)
        return super().convert_field(obj, conversion)

    def format_field(self, obj, format_spec):
        if is_field(obj):
            obj.spec = format_spec
            return str(self.format_field_obj(obj))
        return super().format_field(obj, format_spec)


    '''

    Added convenience methods

    '''

    def missing_field(self, e, key, a, kw):
        '''This is fired as soon as a KeyError or IndexError is raised in ``get_field``.

        Arguments:
            e (Exception): The error that was raised. Let's you distinguish between
                Key vs Index errors.
            key (str): the key/index that was used.
            a (list): the str.format() positional arguments
            kw (dict): the str.format() keyword arguments

        Returns:
            field (Field): the instantiated field object
            key (str): the key used
        '''
        field = Field(
            error=e,
            # fmtr=self,
            # args=a, kwargs=kw
        )

        # this will drop any format indices
        # how would we partially format with positional args?
        # we'd have to have a counter
        # and how would you deal with `pformat('{1} {0}', 'a')` ?
        # because {1} will be evaluated before {0}
        # oh but we could just do `key - len(a)`
        # also, I'd like to retain not having the index if it
        # wasn't specified in the first place
        # also, not sure how to deal with complex keys [0].name[1].blah
        if not isinstance(e, IndexError):
            field.key = key
        return field, key


    def missing_field_value(self, obj):
        '''Get the value for a field missing format arguments.

        Arguments:
            obj (Field): the current field object - has access to the entire field data.

        Returns:
            whatever should be inserted back into the format string.
        '''
        return _NoValue

    def convert_field_obj(self, obj):
        '''Runs after ``convert_field`` is run on a Field.

        Arguments:
            obj (Field): the current field object - has access to the entire field data.

        Returns:
            obj (Field): the modified field. Or whatever final value you want
        '''
        return obj

    def format_field_obj(self, obj):
        '''Runs after ``format_field`` is run on a Field.

        Arguments:
            obj (Field): the current field object - has access to the entire field data.

        Returns:
            value (str): the final formatted value.

        Raises:
            Exception thrown in ``get_field`` if the value is still missing and
            no missing value is set.
        '''
        if obj.missing:
            obj.value = self.missing_field_value(obj)
        val = self.get_formatted_field_value(obj)
        if not is_value(val) and obj.error:
            raise obj.error
        return val

    def get_formatted_field_value(self, field):
        '''Essentially runs the full format pipeline ``get_field``, ``convert_field``,
        ``format_field`` after accumulating all of the format components.

        Arguments:
            obj (Field): the current field object - has access to the entire field data.

        Returns:
            value (str): the final formatted value.

        '''
        if is_value(field.value):
            return field.value

        val = field.obj
        if is_value(val):
            if field.conv:
                val = self.convert_field(val, field.conv)
            if field.spec:
                val = self.format_field(val, field.spec)
        return val


'''

Field abstraction.

'''

class Field:
    '''This is used to mark a field of interest.'''
    def __init__(self, key=None, conv=None, spec=None, value=_NoValue,
                 obj=_NoValue, error=None, args=None, kwargs=None):
        (
            # parsed field parts
            self.key, self.conv, self.spec,
            # field value
            self.value, self.obj,
            # meta
            self.error, self.args, self.kwargs,
        ) = (
            key, conv, spec, value, obj, error, args, kwargs,
        )

    @property
    def missing(self):
        return get_first_value(self.value, self.obj) is _NoValue

    @property
    def field(self):
        return ('{' + (
            (self.key or '') +
            ('!' + self.conv if self.conv else '') +
            (':' + self.spec if self.spec else '')
        ) + '}')

    def __repr__(self):
        return '<Field {} value={} obj={}'.format(self.field, self.value, self.obj)

    # def __str__(self):
    #     # XXX: self.obj
    #     return str(get_first_value(self.value, self.field))

def is_value(value):
    return value is not _NoValue

def is_field(obj):
    return isinstance(obj, Field)

def get_first_value(*vals):
    return next((v for v in vals if is_value(v)), _NoValue)
