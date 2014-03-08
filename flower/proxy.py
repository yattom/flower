import operator
class Proxy(object):
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

    def __init__(self, subject):
        self.__v = Proxy.Storage()
        self.__v.subject = subject
        self.__v.operations = []

    def __getattr__(self, name):
        print "attr: " + name
        subj = self.__v.operations[-1][1] if self.__v.operations else self.__v.subject
        op = Proxy.Attr(name)
        val = op.evaluate(subj)
        self.__v.operations.append((op, val))
        return self

    def __getitem__(self, idx):
        subj = self.__v.operations[-1][1] if self.__v.operations else self.__v.subject
        op = Proxy.GetItem(idx)
        val = op.evaluate(subj)
        self.__v.operations.append((op, val))
        return self

    def __call__(self, *args, **kwargs):
        subj = self.__v.operations[-1][1] if self.__v.operations else self.__v.subject
        op = Proxy.Call(args, kwargs)
        val = op.evaluate(subj)
        self.__v.operations.append((op, val))
        return self

    def current(self):
        subj = self.__v.subject
        for op, _ in self.__v.operations:
            subj = op.evaluate(subj)
        return subj

    def before(self):
        subj = self.__v.operations[-1][1] if self.__v.operations else self.__v.subject
        return subj



