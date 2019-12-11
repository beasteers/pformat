'''Partial formatting, and more

'''

from . import core

# name shortcuts
PARTIAL = core.PartialFormatter
GLOB = core.GlobFormatter
REGEX = core.RegexFormatter
DEFAULT = core.DefaultFormatter


# Initialize default formatters
pformat = core.PartialFormatter().format
gformat = core.GlobFormatter().format
reformat = core.RegexFormatter().format
dformat = core.DefaultFormatter().format
