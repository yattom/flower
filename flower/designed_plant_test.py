import unittest
from hamcrest import *
from hamcrest.core.base_matcher import BaseMatcher

#from soil import *
from designed_plant import *

def tickn(n = 1):
    for i in range(n):
        World.tick()


class Params(object):
    seed = {
        'pooled_water_to_root': 100,
        'water_for_seed': 10,
        'length_to_sprout': 1.0,
        'pooled_water_to_sprout': 200,
    }

    root = {
        'take_in_per_volume': Materials({'water': 10.0, 'heplon': 2.0}),
        'growth': {
            'default': {
                'max_volume': 2.0,
                'consumption_for_growth': Materials({'kledis': 1.0}),
                'growth_volume': 0.1,
            }
        },
    }

    stem = {
        'growth': {
            'default': {
                'max_volume': 0.5,
                'consumption_for_growth': Materials({'kledis': 3.0}),
                'growth_volume': 0.1,
            }
        }
    }

    leaves = {
        'take_in': Materials({'mygen': 1.0}),
        'consumption_for_synthesis': Materials({'mygen': 1.0, 'heplon': 1.0}),
        'produce_for_synthesis': Materials({'kledis': 1.0}),
        'growth': {
            'default': {
                'consumption_for_growth': Materials({}),
                'growth_volume': 0.1,
            }
        }
    }

    flower = {
        'growth': {
            'default': {
                'growth_volume': 0.0,
            }
        },
        'generation': {
            'pollen': {
                'max_count': 10,
                'source_material': Materials({'kledis': 1.0}),
                'part_type': Pollen,
            },
            'egg': {
                'max_count': 1,
                'source_material': Materials({'kledis': 1.0}),
                'part_type': Egg,
            }
        },
    }

    egg = {
        'growth': {
            'to_ripe': {
                'max_volume': 5.0,
                'consumption_for_growth': Materials({'kledis': 1.0}),
                'growth_volume': 1.0,
            },
            'fertilized': {
                'max_volume': 10.0,
                'consumption_for_growth': Materials({'kledis': 1.0}),
                'growth_volume': 1.0,
            },
            'seeded': {
                'growth_volume': 0.0,
            }
        }
    }



class HasPart(BaseMatcher):
    def __init__(self, part_name):
        self.part_name = part_name

    def _matches(self, item):
        return len(item._vein.part(self.part_name)) > 0

    def describe_to(self, descripition):
        descripition.append_text('has part "%s"'%(self.part_name))

def has_part(name):
    return HasPart(name)

def has_no_part(name):
    return is_not(has_part(name))

class DesignedPlantTest(unittest.TestCase):
    def setUp(self):
        World.reset()

    def test_planting_a_seed(self):
        seed = Seed({}, PlantParameters({'root': { 'growth': {}}, 'stem': {'growth': {}}}))
        seed.root()
        seed.sprout()

        assert_that(seed._vein.pooled()['water'], is_(0))
        seed._root.take_in_from_environment({'water': 100})
        assert_that(seed._vein.pooled()['water'], is_(100))
        seed._stem.consume_material(Materials({'water': 10}))
        assert_that(seed._vein.pooled()['water'], is_(90))

    def test_all_growth(self):
        ground = Ground(size=(1000.0, 1000.0), depth=(10.0))
        seed = Seed(
            {'kledis': 100.0},
            PlantParameters({
                'seed': Params.seed,
                'root': Params.root,
                'stem': Params.stem,
                'leaves': Params.leaves,
            }))
        ground.plant(seed, location=(500.0, 500.0))

        assert_that(seed, has_part('seed'))
        assert_that(seed, has_no_part('root'))

        tickn(10)
        assert_that(seed, has_part('root'), 'a new root is sprouted')

        i = 0
        while not seed._vein.part('stem'):
            assert_that(seed._vein.part('root')[0].growth.volume, close_to(i * 0.1, 0.01))
            tickn()
            i += 1

        assert_that(seed, has_part('stem'), 'a new stem is sprouted')

        while not seed._vein.part('leaves'):
            tickn()
        assert_that(seed, has_part('leaves'), 'a new leaves is sprouted')

        old_kledis_amount = seed._vein.pooled()['kledis']
        leaves_volume = seed._vein.part('leaves')[0].growth.volume
        tickn()
        tickn(30)
        assert_that(seed._vein.pooled()['kledis'], is_(greater_than(old_kledis_amount)), 'leaves generate kledis')

    def test_leaves_synthesize_more_as_grow(self):
        leaves = Leaves(
            Vein(),
            PlantParameters({
                'leaves': Params.leaves,
            }))
        leaves.take_in_from_environment(Materials({'kledis': 100, 'mygen': 100.0, 'heplon': 100.0}))

        leaves_volume = leaves.growth.volume
        tickn()
        leaves_volume_delta_first = leaves.growth.volume - leaves_volume
        tickn(10)
        assert_that(leaves.growth.volume, greater_than(leaves_volume))
        leaves_volume_2 = leaves.growth.volume
        tickn()
        leaves_volume_delta_last = leaves.growth.volume - leaves_volume
        assert_that(leaves_volume_delta_last, greater_than(leaves_volume_delta_first))



class FlowerTest(unittest.TestCase):
    def setUp(self):
        World.reset()
        vein = Vein()
        self.flower = Flower(vein, PlantParameters({
            'seed': Params.seed,
            'root': Params.root,
            'stem': Params.stem,
            'flower': Params.flower,
            'egg': Params.egg,
        }))

    def test_bloom_with_enough_nourishment(self):
        self.flower.take_in_from_environment({'kledis': 20.0})
        assert_that(self.flower._vein.part('pollen'), is_([]))
        assert_that(self.flower._vein.part('egg'), is_([]))
        assert_that(self.flower.is_blooming, is_(False))
        tickn(10)
        assert_that(self.flower._vein.pooled()['kledis'], less_than(20.0))
        assert_that(self.flower._vein.part('pollen'), has_length(10))
        assert_that(self.flower._vein.part('egg'), has_length(1))
        assert_that(self.flower.is_blooming, is_(True))

    def test_egg_does_not_grow_unless_fertilized(self):
        self.flower.take_in_from_environment({'kledis': 20.0})
        tickn(10)
        egg = self.flower._vein.part('egg')[0]
        assert_that(egg.growth.volume, equal_to(5.0))

    def test_egg_and_pollen_produces_seeds(self):
        self.flower.take_in_from_environment({'kledis': 21.0})
        tickn(10)
        pollen = self.flower._vein.part('pollen')[0]
        egg = self.flower._vein.part('egg')[0]
        reproducing = ReproducingRule()
        assert_that(reproducing.can_mate(egg, pollen), is_(True))
        reproducing.mate(egg, pollen)
        assert_that(egg.fertilized, is_(True))
        assert_that(pollen.destroyed, is_(True))
        tickn(10)
        assert_that(egg.growth.volume, equal_to(10.0))
        assert_that(egg.seed, is_not(None))

    def test_produced_seeds_will_live(self):
        self.flower.take_in_from_environment({'kledis': 21.0})
        tickn(10)
        pollen = self.flower._vein.part('pollen')[0]
        egg = self.flower._vein.part('egg')[0]
        ReproducingRule().mate(egg, pollen)
        tickn(10)

        seed = egg.seed
        assert_that(seed._vein, is_not(self.flower._vein), 'produced seed has its own vein')
        assert_that(seed._vein.part('root'), is_([]))
        tickn(10)
        assert_that(seed._vein.part('root'), is_not([]), 'a new root is sprouted')
