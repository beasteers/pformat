'''
# Fancy string formatting:


'''
import string
from .base import _NoValue, Formatter, Field, is_field


class PartialFormatter(Formatter):
    '''Partial string formatting!! Finally!

    Examples:
    >>> f = lambda x, *a, **kw: (x, pformat(x, *a, **kw))

    >>> print(f('{a}/b/{c}/d/{e}',          e='eee'))
    ... print(f('{a:s}/b/{c!s:s}/d/{e}',    e='eee'))
    ... print(f('{}/b/{}/d/{}',             'aaa', 'ccc'))
    ... print(f('{:s}/b/{}/d/{:s}',         'aaa', 'ccc'))
    ...
    ('{a}/b/{c}/d/{e}', '{a}/b/{c}/d/eee')
    ('{}/b/{}/d/{}', 'aaa/b/ccc/d/{}')
    ('{a:s}/b/{c!s:s}/d/{e}', '{a:s}/b/{c!s:s}/d/eee')
    ('{:s}/b/{}/d/{:s}', 'aaa/b/ccc/d/{:s}')

    ## Partial Formatting:

    ### The Problem:
    You have multiple variables that you want to substitute in
    ```python
    name = '{param1}_{param2}/{id}/{loss:.2f}.csv'

    def run_hypersearch(name, params):
        for p in params:
            name_i = name.format(**p)
            os.makedirs(os.path.dirname(name_i))
            run_test(name_i, build_experiments(**p), p)

    IDS = [...]

    def run_test(name, exps, format_args):
        for id in IDS:
            do_something_and_write_to_file(exps[id], name, dict(format_args, id=id))


    def do_something_and_write_to_file(exp, name, format_args):
        ...


    run_hypersearch(name, [{}, ...])

    ```

    ### The Solution
    ```python
    name = '{param1}_{param2}/{id}{loss:.2f}.csv'

    def run_hypersearch(name, params):
        for p in params:
            name_i = pf.pformat(name, **p)
            os.makedirs(os.path.dirname(name_i))
            run_test(name_i, build_experiments(**p))

    IDS = [...]

    def run_test(name, exps):
        for id in IDS:
            do_something_and_write_to_file(exps[id], pf.pformat(name, id=id))

    run_hypersearch(name, [{}, ...])
    ```


    '''
    def missing_field_value(self, obj):
        return obj.field


class GlobFormatter(Formatter):
    '''
    ## Glob Formatting:

    For any missing keys, an asterisk will be inserted indicating a wildcard for glob searching.

    ### The Problem:
    You want to define a file pattern that works to define a single file or a glob
    pattern of files.

    ```python
    import glob

    file_pattern = '{}/loss_{}'
    file = file_pattern.format('abc', 1/3.)
    assert file == 'abc/loss_0.3333333333333333333'
    ```

    So then you say: "I only really want two decimal places of accuracy".
    ```python
    file_pattern = '{}/loss_{:.2f}'
    assert file_pattern.format('abc', 1/3.) == 'abc/loss_0.33'
    ```

    Works, but,,, now you want to get all files matching the pattern:
    ```python
    assert file_pattern.format('abc', '*') == 'abc/loss_*'
    # raises ValueError because '*' can't be formatted using `:.2f`
    ```

    ### The Solution:
    Using `pformat.gformat`, any missing keys will be replaced with an asterisk.
    ```python
    import pformat as pf

    file_pattern = '{}/loss_{:.2f}'
    assert pf.gformat(file_pattern, 'abc', 1/3.) == 'abc/loss_0.33'
    assert pf.gformat(file_pattern, 'abc') == 'abc/loss_*'
    ```

    '''
    def missing_field_value(self, obj):
        return '*'


class RegexFormatter(string.Formatter):
    '''Regex match formatting
    Make sure that a string matches a regular expression before inserting.

    Example
    -------
    >>> rformat(r'{i:/\\d[^\\d]*/}', i='3aasdfasdf')
    '3aasdfasdf'
    >>> rformat(r'{i:/\\d[^\\d]*/}', i='a3aasdfasdf')
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    ...
    ValueError: Input (a3aasdfasdf) did not match the regex pattern `/\\d[^\\d]*/`
    '''
    def format_field(self, obj, format_spec):
        import re
        if format_spec.startswith('/') and format_spec.endswith('/'):
            obj = str(obj) # coerce to string for re
            if not re.match(format_spec[1:-1], obj):
                raise ValueError(
                    'Input ({}) did not match the regex pattern ({})'.format(
                        obj, format_spec))

            return obj
        return super().format_field(obj, format_spec)


# formatter_field_name_split = string.Formatter.__module__._string.formatter_field_name_split

class DefaultFormatter(Formatter):
    '''
    ## Default Value Formatting:

    As a generalization of Glob Formatting, you can specify a custom default
    value for each field within the format string.

    ## The Problem:
    You're wishing that you could specify default values per field, but it's cumbersome
    to handle, especially with type specific format rules
    ```python
    file_pattern = '{name}/loss_{loss:.2f}'
    assert file_pattern.format(name='abc', loss=1/3.) == 'abc/loss_0.33'
    assert file_pattern.format(name='abc') == 'abc/loss_'
    # raises KeyError - missing `loss`
    assert file_pattern.format(name='abc', loss=results.get('loss', '--')) == 'abc/loss_--'
    # raises ValueError - can't format '--' using `:.2f`
    ```

    ### The Solution:
    Using `pformat.dformat`, default values can be specified which bypass the format rules.
    ```python
    import pformat as pf

    file_pattern = '{name}/loss_{loss._[--]:.2f}'
    assert file_pattern.format(name='abc', loss=1/3.) == 'abc/loss_0.33'
    assert file_pattern.format(name='abc') == 'abc/loss_--'
    ```

    ```python

    ```
    '''
    DEFAULT_ATTR = '_'

    def get_default_pattern_key_value(self, key):
        rest = list(string._string.formatter_field_name_split(key)[1])

        if len(rest) >= 2:
            # check the last two attributes to see if it matches: *._[default_value]
            [(is_attr1, val1), (is_attr2, val2)] = rest[-2:]
            if not is_attr2 and (
                    self.DEFAULT_ATTR or is_attr1 and val1 == self.DEFAULT_ATTR):

                # split off the default value
                split_id = ('.{}'.format(self.DEFAULT_ATTR)
                            if self.DEFAULT_ATTR else '') + '['

                key2 = key.rsplit(split_id, 1)[0]
                return key2, val2
        return None, None


    def missing_field(self, e, key, a, kw):
        # get key minus the default indicator + value
        # e.g. {x._[no value]} => {x} where "no value" will be returned if x is missing
        # basically: `key2, val2 = 'x', 'no value'`
        key2, val2 = self.get_default_pattern_key_value(key)
        if key2:
            # get the field using the modified key
            field, key3 = super().get_field(key2, a, kw)
            # if is still a missing field
            if is_field(field) and field.missing:
                # use default value (and original key)
                field.key, field.value = key, val2
                return field, key
            return field, key3

        # no default
        return super().missing_field(e, key, a, kw)


def multiformatter(*formatters):
    '''
    import pformat as pf
    xformat = multiformatter(pf.DEFAULT, pf.PARTIAL).format
    xformat('{x._[--]:.2f}{unit}')
    '''
    return type('MultiFormatter', tuple(*formatters), {})
