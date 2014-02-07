# coding: utf-8

from event import EventDispatcher

from soil import *

class PlantPart(WorldEntity):
    def __init__(self, name, vein, params):
        super(PlantPart, self).__init__()
        self._vein = vein
        self._vein.connect(name, self)
        self._fixed_materials = Materials()
        self._params = params

    def take_in_from_environment(self, materials):
        self._vein.pour_in(materials, source=self)

    def consume_material(self, materials):
        assert self._vein.pooled() >= materials
        pumped_out = self._vein.pump_out(materials, self)
        self._fixed_materials.add(pumped_out)

    def produce_material(self, product, source):
        for name in source:
            assert self._vein.pooled()[name] >= source[name]
        self._vein.pump_out(source, self)
        self._vein.pour_in(product, source=self)

    def generate_part(self, cls):
        return cls(self._vein, self._params)

    def state(self):
        return None


class Growth(object):
    EVENTS = ['ON_MAXED']

    def __init__(self, target, params):
        self._target = target
        self._params = params
        self.volume = 0.0
        self.events = EventDispatcher(Growth.EVENTS, observer=target)

    def grow(self):
        params = self.current_params()
        if params.growth_volume == 0.0 or self.maxed_out(): return

        self._target.consume_material(params.consumption_for_growth)
        self.volume += params.growth_volume
        if self.maxed_out():
            self.volume = params.max_volume
            self.events.trigger(self.events.ON_MAXED)

    def current_params(self):
        params = self._params.get(self._target.state(), None)
        if not params: params = self._params['default'] 
        return params

    def maxed_out(self):
        return self.current_params().has_max_volume and self.volume >= self.current_params().max_volume


class PlantPartGeneration(object):
    def __init__(self, target, params):
        self._target = target
        self._params = params
        self._generated = []

    def tick(self):
        if self.maxed_out(): return

        if self._target._vein.pooled() >= self._params.source_material:
            generated = self._target.generate_part(self._params.part_type)
            generated.consume_material(self._params.source_material)
            self._generated.append(generated)

    def maxed_out(self):
        return self._params.has_key('max_count') and len(self._generated) >= self._params['max_count']


class ConventionalDict(object):
    def __init__(self, d):
        self._d = d

    def __getitem__(self, key):
        if key and key.startswith('has_'):
            return self._d.has_key(key[len('has_'):])
        value = self._d.get(key)
        if isinstance(value, dict):
            return ConventionalDict(value)
        return value

    def __getattr__(self, name):
        return self[name]

    def get(self, key, default=None):
        value = self[key]
        return value if value else default

    def has_key(self, key):
        return self._d.has_key(key)


class PlantParameters(ConventionalDict):
    def __init__(self, params):
        super(PlantParameters, self).__init__(params)
