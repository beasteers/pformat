# pformat
Partial string formatting, among other things.

This repo is meant to facilitate augmentations for normal Python string formatting. We support:
 - partial formatting: missing keys will remain so they can be formatted later.
 - glob formatting: missing keys will be replaced with `*` as if the format string is an underspecified file path.
 - default formatting: missing keys will be replaced by a default value specified within the format string:
    - e.g. `'/blah/blorp/{time._[~unknown~]:.2f}'` will set `time='~unknown~'` if not found. It even works if there is a type specific format string (e.g. decimal place specification). This is a carefully chosen syntax that will maintain syntax highlighting (at least in Atom).
 - regex formatting: checks if the key matches a regex and throws an error if not. This is incomplete and I really meant it to be used for string parsing/reverse string formatting See parser (TODO add repo).

## Install

```bash
pip install pformat
```

## Usage
```python
import pformat as pf

# partial formatting
result = pformat('/blah/blorp/{time:.2f}/{id}.csv', id=100)
assert result == '/blah/blorp/{time:.2f}/100.csv'

# glob formatting
result = pformat('/blah/blorp/{time:.2f}/{id}.csv', time=time.time())
assert result == '/blah/blorp/1500000.00/*.csv'

# default formatting
result = pformat('/blah/blorp/{time:.2f}/{id._[thing]}.csv', time=time.time())
assert result == '/blah/blorp/1500000.00/thing.csv'

```
