# tool was originally made with python 3.3, this file contains small hacks which make the tool compatible with python 3.10

import collections
import collections.abc
import monotonic
collections.Mapping = collections.abc.Mapping

import six

f = six.raise_from
def func(*args):
    if len(args) == 0:
        raise AttributeError()
    e = args[0]
    e2 = e.args[0] if len(e.args) != 0 else None
    raise e from e2
six.raise_from = func

monontic = monotonic