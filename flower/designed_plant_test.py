import unittest
from hamcrest import *

#from soil import *
from designed_plant import *

def tickn(n = 1):
    for i in range(n):
        World.tick()

class DesignedPlantTest(unittest.TestCase):
    def setUp(self):
        World.reset()

    def test_plant(self):
        seed = Seed({}, {'root': { 'growth': {}}, 'stem': {'growth': {}}})
        seed.root()
        seed.sprout()

        assert_that(seed._vein.pooled('moisture'), is_(0))
        seed._root.take_in_from_environment({'moisture': 100})
        assert_that(seed._vein.pooled('moisture'), is_(100))
        seed._stem.consume_material({'moisture': 10})
        assert_that(seed._vein.pooled('moisture'), is_(90))

    def test_all_growth(self):
        ground = Ground(size=(1000.0, 1000.0), depth=(10.0))
        seed = Seed(
            {'kledis': 100.0},
            {
                'seed': {
                    'pooled_water_to_root': 100,
                    'moisture_for_seed': 10,
                    'length_to_sprout': 1.0,
                    'pooled_water_to_sprout': 200,
                },
                'root': {
                    'take_in_per_volume': Materials({'moisture': 10.0, 'heplon': 2.0}),
                    'growth': {
                        'max_volume': 2.0,
                        'consumption_for_growth': Materials({'kledis': 1.0}),
                        'growth_volume': 0.1,
                    },
                },
                'stem': {
                    'growth': {
                        'max_volume': 0.5,
                        'consumption_for_growth': Materials({'kledis': 3.0}),
                        'growth_volume': 0.1,
                    }
                },
                'leaves': {
                    'take_in': Materials({'mygen': 1.0}),
                    'consumption_for_synthesis': Materials({'mygen': 1.0, 'heplon': 1.0}),
                    'produce_for_synthesis': Materials({'kledis': 1.0}),
                },
            })
        ground.plant(seed, location=(500.0, 500.0))

        assert_that(seed._vein.part('root'), is_([]))

        tickn(10)
        assert_that(seed._vein.part('root'), is_not([]), 'a new root is sprouted')

        i = 0
        while not seed._vein.part('stem'):
            assert_that(seed._vein.part('root')[0].growth.volume, close_to(i * 0.1, 0.01))
            tickn()
            i += 1

        assert_that(seed._vein.part('stem'), is_not([]), 'a new stem sprouted')

        while not seed._vein.part('leaves'):
            tickn()
        assert_that(seed._vein.part('leaves'), is_not([]), 'new leaves are generated')

        old_kledis_amount = seed._vein.pooled('kledis')
        tickn(30)
        assert_that(seed._vein.pooled('kledis'), is_(greater_than(old_kledis_amount)), 'leaves generate kledis')


class FlowerTest(unittest.TestCase):
    def setUp(self):
        World.reset()
        vein = Vein()
        self.flower = Flower(vein, {
            'egg': {
                'growth': {
                    'max_volume': 5.0,
                    'consumption_for_growth': Materials({'kledis': 1.0}),
                    'growth_volume': 1.0,
                }
            }
        })

    def test_bloom_with_enough_nourishment(self):
        self.flower.take_in_from_environment({'kledis': 20.0})
        assert_that(self.flower._vein.part('pollen'), is_([]))
        assert_that(self.flower._vein.part('egg'), is_([]))
        assert_that(self.flower.is_blooming, is_(False))
        tickn(10)
        assert_that(self.flower._vein.pooled('kledis'), less_than(20.0))
        assert_that(self.flower._vein.part('pollen'), has_length(10))
        assert_that(self.flower._vein.part('egg'), has_length(1))
        assert_that(self.flower.is_blooming, is_(True))
