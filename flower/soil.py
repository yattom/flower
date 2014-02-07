# coding: utf-8

class Materials(object):
    NAMES = ['kledis', 'heplon', 'mygen', 'moisture']

    def __init__(self, d=None):
        self._contents = d if d else {}

    def __getitem__(self, key):
        return self._contents.get(key, 0)

    def __setitem__(self, key, val):
        self._contents[key] = val

    def add(self, materials):
        for name in materials:
            self[name] += materials[name]

    def empty(self):
        self._contents.clear()

    def __iter__(self):
        return self._contents.__iter__()

    def __repr__(self):
        return 'Materials(%s)'%(repr(self._contents))

    def __mul__(self, number):
        return Materials(dict([(k, self._contents[k] * number) for k in self._contents]))

    def __eq__(self, other):
        return self._contents == other._contents

    def __lt__(self, other):
        return all(self[name] < other[name] for name in Materials.NAMES)

    def __le__(self, other):
        return all(self[name] <= other[name] for name in Materials.NAMES)

    def __gt__(self, other):
        return all(self[name] > other[name] for name in Materials.NAMES)

    def __ge__(self, other):
        return all(self[name] >= other[name] for name in Materials.NAMES)

class World(object):
    entities = []
    entities_to_add_after_tick = []
    tick_in_progress = False

    @staticmethod
    def tick():
        World.tick_in_progress = True
        try:
            for e in World.entities:
                e.tick()
        finally:
            World.tick_in_progress = False
            World._add_entities_after_tick()

    @staticmethod
    def _add_entities_after_tick():
        for e in World.entities_to_add_after_tick:
            World.add(e)
        del(World.entities_to_add_after_tick[:])

    @staticmethod
    def add(entity):
        if entity in World.entities: return

        if World.tick_in_progress:
            World.entities_to_add_after_tick.append(entity)
            return

        World.entities.append(entity)

    @staticmethod
    def remove(entity):
        if entity not in World.entities: return
        World.entities.remove(entity)

    @staticmethod
    def reset():
        World.entities = []


class WorldEntity(object):
    def __init__(self):
        World.add(self)

    def tick(self):
        pass

    def remove(self):
        World.remove(self)
        self.destroyed = True


class Vein(object):
    def __init__(self):
        self._pooled = Materials()
        self._parts = {}

    def connect(self, name, part):
        assert not self.has_part(part), "cannot connect same part twice"
        if name not in self._parts:
            self._parts[name] = []
        self._parts[name].append(part)

    def part(self, name):
        return self._parts.get(name, [])

    def pour_in(self, materials, source):
        assert self.has_part(source)
        for name in materials:
            self._pooled[name] += materials[name]

    def pump_out(self, materials, dest):
        assert self.has_part(dest)
        out = Materials()
        for name in materials:
            self._pooled[name] -= materials[name]
            out[name] += materials[name]
        return out

    def pooled(self):
        return self._pooled

    def has_part(self, part):
        return any([part in parts for parts in self._parts.values()])


class Ground(object):
    def __init__(self, size, depth):
        self.size = size
        self.depth = depth

    def plant(self, target, location):
        pass


def main():
    pass

if __name__=='__main__':
    main()
