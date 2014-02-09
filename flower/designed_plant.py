# coding: utf-8

from pattern import switch

from soil import *
from plant import *

class Seed(PlantPart):
    '''
    This particular plant is grown from a seed
    with water, heplon, kledis, and mygen.
    water is required for most mechanisms
    but not consumed but emitted to environment.
    Helpon and mygen are taken-in from environment
    and mostly converted to kledis by photonic synthesis.
    Mygen can be taken from air and heplon can be taken from earth.
    Kledis is the basic ingredient for almost all of
    structures in plants.  Kledis is also decomposed
    to produce energy and regain heplon and mygen.

    '''

    def __init__(self, initial_contents, params):
        super(Seed, self).__init__('seed', Vein(), params)
        self._vein.pour_in(initial_contents, self)

    def root(self):
        self._root = self.generate_part(Root)

    def sprout(self):
        self._stem = self.generate_part(Stem)

    def tick(self):
        switch(self.state(),
               'seed', self.tick_for_seed,
               'rooted', self.tick_for_rooted,
               'sprouted', self.tick_for_sprouted)

    def tick_for_seed(self):
        self.take_in_from_environment({'water': self._params.seed.water_for_seed})
        if self._vein.pooled()['water'] >= self._params.seed.pooled_water_to_root:
            self.root()

    def tick_for_rooted(self):
        for root in self._vein.part('root'):
            if root.growth.volume >= self._params.seed.length_to_sprout and self._vein.pooled()['water'] >= self._params.seed.pooled_water_to_sprout:
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


class Root(PlantPart):
    def __init__(self, vein, params):
        super(Root, self).__init__('root', vein, params)
        self.growth = Growth(self, params.root.growth)

    def tick(self):
        self.take_in_from_environment(self._params['root']['take_in_per_volume'] * self.growth.volume)
        self.growth.grow()


class Stem(PlantPart):
    def __init__(self, vein, params):
        super(Stem, self).__init__('stem', vein, params)
        self.growth = Growth(self, params.stem.growth)
        self._leaves = None

    def tick(self):
        self.growth.grow()

    @EventDispatcher.event_handler
    def on_maxed(self):
        if self._leaves: return
        self._leaves = self.generate_part(Leaves)


class Leaves(PlantPart):
    def __init__(self, vein, params):
        super(Leaves, self).__init__('leaves', vein, params)
        self.growth = Growth(self, params.leaves.growth)

    def tick(self):
        self.growth.grow()
        self.take_in_from_environment(self._params.leaves.take_in * self.growth.volume)
        self.produce_material(self._params.leaves.produce_for_synthesis * self.growth.volume, self._params.leaves.consumption_for_synthesis * self.growth.volume)


class Flower(PlantPart):
    def __init__(self, vein, params):
        super(Flower, self).__init__('flower', vein, params)
        self.pollen_generation = PlantPartGeneration(self, params.flower.generation.pollen)
        self.egg_generation = PlantPartGeneration(self, params.flower.generation.egg)
        self.is_blooming = False

    def tick(self):
        self.pollen_generation.tick()
        self.egg_generation.tick()

        if self.pollen_generation.maxed_out() and self.egg_generation.maxed_out() and self.egg_generation._generated[0].is_ripen:
            # once bloomed, stays in that status
            self.is_blooming = True


class Pollen(PlantPart):
    def __init__(self, vein, params):
        super(Pollen, self).__init__('pollen', vein, params)


class Egg(PlantPart):
    def __init__(self, vein, params):
        super(Egg, self).__init__('egg', vein, params)
        self.growth = Growth(self, params.egg.growth)
        self.is_ripen = False
        self.fertilized = False
        self.seed = None

    def tick(self):
        self.growth.grow()

    @EventDispatcher.event_handler
    def on_maxed(self):
        if self.state() == 'to_ripe':
            self.is_ripen = True
        elif self.state() == 'fertilized':
            self.seed = Seed({}, self._params)
            self.seed.take_in_from_environment(self._fixed_materials)
            self._fixed_materials.clear()

    def state(self):
        if self.seed: return 'seeded'
        if self.fertilized: return 'fertilized'
        return 'to_ripe'

class ReproducingRule(object):
    def can_mate(self, egg, pollen):
        if isinstance(egg, Egg) and isinstance(pollen, Pollen):
            return True
        return False

    def mate(self, egg, pollen):
        egg.fertilized = True
        pollen.remove()
        return
