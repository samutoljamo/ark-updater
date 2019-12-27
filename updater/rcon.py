from valve.rcon import RCON as r
from valve.rcon import RCONMessage, RCONError, RCONTimeoutError

import functools

class RCON(r):
    def _ensure(state, value=True):  # pylint: disable=no-self-argument
        """Decorator to ensure a connection is in a specific state.

        Use this to wrap a method so that it'll only be executed when
        certain attributes are set to ``True`` or ``False``. The returned
        function will raise :exc:`RCONError` if the condition is not met.

        Additionally, this decorator will modify the docstring of the
        wrapped function to include a sphinx-style ``:raises:`` directive
        documenting the valid state for the call.

        :param str state: the state attribute to check.
        :param bool value: the required value for the attribute.
        """

        def decorator(function):  # pylint: disable=missing-docstring

            @functools.wraps(function)
            def wrapper(instance, *args, **kwargs):  # pylint: disable=missing-docstring
                if getattr(instance, state) is not value:
                    raise RCONError("Must {} {}".format(
                        "be" if value else "not be", state))
                return function(instance, *args, **kwargs)
            return wrapper

        return decorator
    @_ensure('connected')
    @_ensure('authenticated')
    def execute(self, command, block=True, timeout=None):
        if timeout is None:
            timeout = self._timeout
        self._request(RCONMessage.Type.EXECCOMMAND, command)
        if block:
            try:
                return self._receive(timeout)
            except RCONTimeoutError:
                self._responses.discard()
                raise
        else:
            self._responses.discard()
            self._read()

