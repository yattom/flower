# coding: utf-8

class Materials(object):
    def __init__(self, d=None):
        self.__contents = d if d else {}

    def __getitem__(self, key):
        return self.__contents.get(key, 0)

    def __setitem__(self, key, val):
        self.__contents[key] = val

    def add(self, materials):
        for name in materials:
            self[name] += materials[name]

    def __iter__(self):
        return self.__contents.__iter__()

    def __repr__(self):
        return 'Materials(%s)'%(repr(self.__contents))

    def __mul__(self, number):
        return Materials(dict([(k, self.__contents[k] * number) for k in self.__contents]))

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
            World.add_entities_after_tick()

    @staticmethod
    def add_entities_after_tick():
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
    def reset():
        World.entities = []


class WorldEntity(object):
    def __init__(self):
        World.add(self)

    def tick(self):
        pass


class PlantPart(WorldEntity):
    def __init__(self, name, vein, form_params):
        super(PlantPart, self).__init__()
        self._vein = vein
        self._vein.connect(name, self)
        self.fixed_materials = Materials()
        self.form_params = form_params

    def take_in_from_environment(self, materials):
        self._vein.pour_in(materials, source=self)

    def consume_material(self, materials):
        for name in materials:
            assert self._vein.pooled(name) >= materials[name]
        pumped_out = self._vein.pump_out(materials, self)
        self.fixed_materials.add(pumped_out)

    def produce_material(self, dest, src):
        for name in src:
            assert self._vein.pooled(name) >= src[name]
        self._vein.pump_out(src, self)
        self._vein.pour_in(dest, source=self)

    def generate_part(self, cls):
        return cls(self._vein, self.form_params)

class Vein(object):
    def __init__(self):
        self.__pooled = Materials()
        self.__parts = {}

    def connect(self, name, part):
        assert part not in self.__parts
        if name not in self.__parts:
            self.__parts[name] = []
        self.__parts[name].append(part)

    def part(self, name):
        return self.__parts.get(name, [])

    def pour_in(self, materials, source):
        assert source in [i for sublist in self.__parts.values() for i in sublist]
        for name in materials:
            self.__pooled[name] += materials[name]

    def pump_out(self, materials, dest):
        assert dest in [i for sublist in self.__parts.values() for i in sublist]
        out = Materials()
        for name in materials:
            self.__pooled[name] -= materials[name]
            out[name] += materials[name]
        return out

    def pooled(self, material):
        return self.__pooled[material]

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
