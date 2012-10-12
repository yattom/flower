class EventDispatcher(object):
    '''
    A simple framework for event handlers or Observer Pattern.


    Define a class for observers and handler methods.
    Event handlers' names must be the lower case of the event name.
    >>> class Observer(object):
    ...   @EventDispatcher.event_handler
    ...   def on_click(self):
    ...       print 'Observer.on_click!'
    ...   @EventDispatcher.event_handler
    ...   def on_focus(self):
    ...       print 'Observer.on_focus!'

    Define events in EventDispatcher constructor.
    event_names must be in all uppercase.
    >>> events = EventDispatcher(['ON_CLICK', 'ON_FOCUS', 'NO_HANDLER'], observer=Observer())

    Use trigger() to invoke handlers.  Event name constants are
    automatically defined for convenience so use them to avoid
    typo related bugs.
    >>> events.trigger(events.ON_CLICK)
    Observer.on_click!
    >>> events.trigger(events.ON_FOCUS)
    Observer.on_focus!

    Nothing happens if no corresnpond handler is defined.
    >>> events.trigger(events.NO_HANDLER)
    >>>

    @EventDispatcher.event_handler decorator is required by design
    because otherwise there will be no indications that they are
    event handlers.

    '''
    def __init__(self, event_names, observer=None):
        assert all([n == n.upper() for n in event_names])
        self.events = dict((s, None) for s in event_names)
        for e in self.events:
            setattr(self, e, e)
        if observer:
            self.observer = observer

    def _set_handler(self, event, handler):
        self.events[event] = handler

    def trigger(self, event):
        if self.events[event]:
            self.events[event]()

    def set_observer(self, target):
        for attr in dir(target):
            if hasattr(getattr(target, attr), '_EventDispatcher__marked_as_event_handler'):
                self._set_handler(attr.upper(), getattr(target, attr))
    observer = property(None, set_observer)

    @staticmethod
    def event_handler(func):
        func.__marked_as_event_handler = True
        return func

