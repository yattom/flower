import unittest
from hamcrest import *
from should_dsl import *

from soil import *

class VeinTest(unittest.TestCase):
    def setUp(self):
        World.reset()

    def test_connect(self):
        vein = Vein()
        part1 = object()
        vein.connect('part1', part1)
        assert_that(vein.part('part1'), is_([part1]))
        vein.part('part1') |should_be.equal_to| [part1]

    def test_connect_multiple_in_same_name(self):
        vein = Vein()
        part1_1 = object()
        part1_2 = object()
        part1_3 = object()
        vein.connect('part1', part1_1)
        vein.connect('part1', part1_2)
        vein.connect('part1', part1_3)
        vein.part('part1') |should_be.equal_to| [part1_1, part1_2, part1_3]

    def test_part_with_zero_result(self):
        vein = Vein()
        vein.part('no such part') |should_be.equal_to| []


class WorldTest(unittest.TestCase):
    def setUp(self):
        World.reset()

    class TestEntity(WorldEntity):
        ticked = False
        ticked_count = 0
        def tick(self):
            self.ticked = True
            self.ticked_count += 1

    def test_tick(self):
        entity = WorldTest.TestEntity()
        assert_that(entity.ticked, is_(False), 'tick is not called')
        World.tick()
        assert_that(entity.ticked, is_(True), 'tick is called')

    def test_tick_add_multiple_times(self):
        entity = WorldTest.TestEntity()
        World.add(entity)
        assert_that(entity.ticked_count, is_(0))
        World.tick()
        assert_that(entity.ticked_count, is_(1), 'tick() is called only once')


if __name__=='__main__':
    unittest.main()
