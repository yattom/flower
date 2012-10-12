# coding: utf-8

from pattern import switch
from event import EventDispatcher

from soil import *

class Seed(PlantPart):
    '''
    This particular plant is grown from a seed
    with moisture, heplon, kledis, and mygen.
    Moisture is required for most mechanisms
    but not consumed but emitted to environment.
    Helpon and mygen are taken-in from environment
    and mostly converted to kledis by photonic synthesis.
    Mygen can be taken from air and heplon can be taken from earth.
    Kledis is the basic ingredient for almost all of
    structures in plants.  Kledis is also decomposed
    to produce energy and regain heplon and mygen.

    '''

    def __init__(self, initial_contents, form_params):
        super(Seed, self).__init__('seed', Vein(), form_params)
        self._vein.pour_in(initial_contents, self)

    def root(self):
        self._root = self.generate_part(Root)
        self._vein.connect('root', self._root)

    def sprout(self):
        self._stem = self.generate_part(Stem)
        self._vein.connect('stem', self._stem)

    def tick(self):
        switch(self.state(),
               'seed', self.tick_for_seed,
               'rooted', self.tick_for_rooted,
               'sprouted', self.tick_for_sprouted)

    def tick_for_seed(self):
        self.take_in_from_environment({'moisture': self.form_params['seed']['moisture_for_seed']})
        if self._vein.pooled('moisture') >= self.form_params['seed']['pooled_water_to_root']:
            self.root()

    def tick_for_rooted(self):
        for root in self._vein.part('root'):
            if root.growth.volume >= self.form_params['seed']['length_to_sprout'] and self._vein.pooled('moisture') >= self.form_params['seed']['pooled_water_to_sprout']:
                self.sprout()
                break

    def tick_for_sprouted(self):
        pass

    def state(self):
        if not self._vein.part('root'):
            return 'seed'
        if not self._vein.part('stem'):
            return 'rooted'
        else:
            return 'sprouted'

class Growth(object):
    EVENTS = ['ON_MAXED']

    def __init__(self, target, params):
        self.target = target
        self.params = params
        self.volume = 0.0
        self.events = EventDispatcher(Growth.EVENTS, observer=target)

    def grow(self):
        if self.params.has_key('max_volume') and self.volume > self.params['max_volume']:
            self.events.trigger(self.events.ON_MAXED)
            return
        self.target.consume_material(self.params['consumption_for_growth'])
        self.volume += self.params['growth_volume']


class Root(PlantPart):
    def __init__(self, vein, form_params):
        super(Root, self).__init__('root', vein, form_params)
        self.growth = Growth(self, form_params['root']['growth'])

    def tick(self):
        self.take_in_from_environment(self.form_params['root']['take_in_per_volume'] * self.growth.volume)
        self.growth.grow()


class Stem(PlantPart):
    def __init__(self, vein, form_params):
        super(Stem, self).__init__('stem', vein, form_params)
        self.growth = Growth(self, form_params['stem']['growth'])
        self._leaves = None

    def tick(self):
        self.growth.grow()

    @EventDispatcher.event_handler
    def on_maxed(self):
        if self._leaves: return
        self._leaves = self.generate_part(Leaves)


class Leaves(PlantPart):
    def __init__(self, vein, form_params):
        super(Leaves, self).__init__('leaves', vein, form_params)
        self._volume = 0.0

    def tick(self):
        self.take_in_from_environment(self.form_params['leaves']['take_in'] * self._volume)
        self.produce_material(self.form_params['leaves']['produce_for_synthesis'] * self._volume, self.form_params['leaves']['consumption_for_synthesis'] * self._volume)
        self.grow()

    def grow(self):
        self._volume += 0.1


class Flower(PlantPart):
    def __init__(self, vein, form_params):
        super(Flower, self).__init__('flower', vein, form_params)
        self.pollens = []
        self.egg = None
        self.is_blooming = False

    def tick(self):
        if len(self.pollens) < 10:
            if self._vein.pooled('kledis') >= 1.0:
                pollen = self.generate_part(Pollen)
                pollen.consume_material(Materials({'kledis': 1.0}))
                self.pollens.append(pollen)
        if not self.egg:
            if self._vein.pooled('kledis') >= 1.0:
                self.egg = self.generate_part(Egg)

        if len(self.pollens) >= 10 and self.egg.is_ripen:
            # once bloomed, stays in that status
            self.is_blooming = True


class Pollen(PlantPart):
    def __init__(self, vein, form_params):
        super(Pollen, self).__init__('pollen', vein, form_params)


class Egg(PlantPart):
    def __init__(self, vein, form_params):
        super(Egg, self).__init__('egg', vein, form_params)
        self.growth = Growth(self, form_params['egg']['growth'])
        self.is_ripen = False

    def tick(self):
        self.growth.grow()

    @EventDispatcher.event_handler
    def on_maxed(self):
        self.is_ripen = True
