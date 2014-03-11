import operator
class Recorder(object):
    '''
    Create a proxy wrapping an arbitrary object.  Calling the proxy
    results in another proxy.  current() will retrieve the actual value.
    >>> d = {'a': 0}
    >>> p_d = Recorder(d)
    >>> a_of_d = p_d['a']
    >>> a_of_d.current()
    0

    Wrapped object can be modified. Recorder remembers the value
    when it first created and it can be read by before().
    >>> d['a'] = 1
    >>> a_of_d.current()
    1
    >>> a_of_d.before()
    0

    Chained invocations all create proxies.  current() works as expected
    also in this case.
    >>> d = {'a': {'x': 1}}
    >>> p_d = Recorder(d)
    >>> a_of_d = p_d['a']
    >>> x_of_a_of_d = p_d['a']['x']
    >>> d['a'] = {'y': 2}
    >>> a_of_d.before()
    {'x': 1}
    >>> a_of_d.current()
    {'y': 2}
    >>> x_of_a_of_d.before()
    1
    >>> x_of_a_of_d.current()
    Traceback (most recent call last):
       ...
    KeyError: 'x'
    '''
    class Storage(object):
        pass

    class Attr(object):
        def __init__(self, name):
            self.name = name
        def evaluate(self, subject):
            return subject.__getattribute__(self.name)

    class GetItem(object):
        def __init__(self, idx):
            self.idx = idx
        def evaluate(self, subject):
            return operator.getitem(subject, self.idx)

    class Call(object):
        def __init__(self, args, kwargs):
            self.args = args
            self.kwargs = kwargs
        def evaluate(self, subject):
            return subject.__call__(*self.args, **self.kwargs)

    def __init__(self, subject, precedes=None, operation=None):
        self.__v = Recorder.Storage()
        self.__v.subject = subject
        self.__v.precedes = precedes
        self.__v.operation = operation

    def __getattr__(self, name):
        op = Recorder.Attr(name)
        val = op.evaluate(self.__v.subject)
        return Recorder(val, self, op)

    def __getitem__(self, idx):
        op = Recorder.GetItem(idx)
        val = op.evaluate(self.__v.subject)
        return Recorder(val, self, op)

    def __call__(self, *args, **kwargs):
        op = Recorder.Call(args, kwargs)
        val = op.evaluate(self.__v.subject)
        return Recorder(val, self, op)

    def current(self):
        if not self.__v.precedes:
            return self.__v.subject
        return self.__v.operation.evaluate(self.__v.precedes.current())

    def before(self):
        return self.__v.subject



