import math, struct

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self): return self._x
    @property
    def y(self): return self._y
    @property
    def z(self): return self._z

    @classmethod
    def new(cls, x=0, y=0, z=0):
        return cls(x, y, z)

    @classmethod
    def from_bytes(cls, data):
        x, y, z = struct.unpack('<3f', data)
        return cls(x, y, z)

    def to_bytes(self):
        return struct.pack('<3f', self._x, self._y, self._z)

    def _coerce(self, other):
        if isinstance(other, Vector3):
            return other._x, other._y, other._z
        return other, other, other

    def __add__(self, other):
        ox, oy, oz = self._coerce(other)
        return Vector3(self._x + ox, self._y + oy, self._z + oz)

    def __sub__(self, other):
        ox, oy, oz = self._coerce(other)
        return Vector3(self._x - ox, self._y - oy, self._z - oz)

    def __mul__(self, other):
        ox, oy, oz = self._coerce(other)
        return Vector3(self._x * ox, self._y * oy, self._z * oz)

    def __truediv__(self, other):
        ox, oy, oz = self._coerce(other)
        return Vector3(self._x / ox, self._y / oy, self._z / oz)

    def __radd__(self, other): return self.__add__(other)
    def __rsub__(self, other):
        ox, oy, oz = self._coerce(other)
        return Vector3(ox - self._x, oy - self._y, oz - self._z)
    def __rmul__(self, other): return self.__mul__(other)
    def __rtruediv__(self, other):
        ox, oy, oz = self._coerce(other)
        return Vector3(ox / self._x, oy / self._y, oz / self._z)

    def __neg__(self):
        return Vector3(-self._x, -self._y, -self._z)

    def __eq__(self, other):
        ox, oy, oz = self._coerce(other)
        return self._x == ox and self._y == oy and self._z == oz

    def __repr__(self):
        return f"Vector3({self._x:.4f}, {self._y:.4f}, {self._z:.4f})"
# mangled