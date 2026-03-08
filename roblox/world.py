from roblox.memory import Memory
from roblox.data.structs import *
import json
import struct # bc yes
nullptr = None


class Enums:
    class NameOcclusion:
        NoOcclusion = 0
        EnemyOcclusion = 1
        OccludeAll = 2

    class HumanoidHealthDisplayType:
        DisplayWhenDamaged = 0
        AlwaysOn = 1
        AlwaysOff = 2

    class HumanoidRigType:
        R6 = 0
        R15 = 1
    
    class HumanoidDisplayDistanceType:
        Viewer = 0
        Subject = 1
        Zero = 2

class CFrame:
    def __init__(self, x, y, z, rx=1, ry=0, rz=0, ux=0, uy=1, uz=0, lx=0, ly=0, lz=-1):
        self._x, self._y, self._z = x, y, z
        self._rx, self._ry, self._rz = rx, ry, rz
        self._ux, self._uy, self._uz = ux, uy, uz
        self._lx, self._ly, self._lz = lx, ly, lz
       # self._has_vectors = True

    @classmethod
    def new(cls, x, y, z):
        cf = cls(x, y, z)
        cf._has_vectors = False
        return cf
    @property
    def Position(self):
        return Vector3(self._x, self._y, self._z)

    @Position.setter
    def Position(self, v):
        self._x, self._y, self._z = v.x, v.y, v.z

    @property
    def RightVector(self):
        return Vector3(self._rx, self._ry, self._rz)

    @RightVector.setter
    def RightVector(self, v):
        self._rx, self._ry, self._rz = v.x, v.y, v.z

    @property
    def LookVector(self):
        return Vector3(self._lx, self._ly, self._lz)

    @LookVector.setter
    def LookVector(self, v):
        self._lx, self._ly, self._lz = v.x, v.y, v.z

    def to_bytes(self):
        return struct.pack('<12f',
            self._x,  self._y,  self._z,
            self._rx, self._ry, self._rz,
            self._ux, self._uy, self._uz,
            self._lx, self._ly, self._lz
        )

    @classmethod
    def from_bytes(cls, data):
        vals = struct.unpack('<12f', data)
        return cls(*vals)

    
with open('./offsets.json', "r") as f:
    offsets = json.load(f)

memory = Memory("Roblox") # we live we love we idk

class Instance:
    def __init__(self, address):
        self.address = address
        self.memory = memory

    def get_children(self):
        children = []
        parent_address = self.address
        try:
            children_ptr = self.memory.read_ptr(parent_address + offsets["Instance"]["ChildrenStart"])
            if not children_ptr:
                return children
            children_end = self.memory.read_ptr(children_ptr + offsets["Instance"]["ChildrenEnd"])
            current_child = self.memory.read_ptr(children_ptr)
            while current_child < children_end:
                child_ptr = self.memory.read_ptr(current_child)
                if child_ptr:
                    children.append(Instance(child_ptr))
                current_child += 0x10
            return children
        except TypeError:
            return []

    @property
    def Name(self):
        ptr = self.memory.read_ptr(self.address + offsets["Instance"]["Name"])
        return self.memory.read_string(ptr)

    @property
    def ClassName(self):
        classdescriptor = self.memory.read_ptr(self.address + offsets["Instance"]["ClassDescriptor"])
        classname = self.memory.read_ptr(classdescriptor + offsets["Instance"]["ClassName"])
        return self.memory.read_string(classname)

    @property
    def Address(self):
        return self.address

    def FindFirstChild(self, name):
        children = self.get_children()
        for i in children:
            if i.Name == name: return i
        return Instance(0)


    def FindFirstChildWhichIsA(self, name):
        children = self.get_children()
        for i in children:
            if i.ClassName == name: return i

    @property
    def LocalPlayer(self):
        return Instance(self.get_children()[0]) # its rivals support

    @property
    def Character(self):
        return Instance(memory.read_ptr(self.address + offsets["Player"]["ModelInstance"]))
    @property
    def Humanoid(self):
        return Instance(self.address).FindFirstChildWhichIsA("Humanoid") # humanoid.Name = "67"
    
    @property
    def WalkSpeed(self):
        return self.memory.read_float(self.address + offsets["Humanoid"]["WalkSpeed"])
    
    @WalkSpeed.setter
    def WalkSpeed(self, val: float) -> None:
        self.memory.write_float(self.address + offsets["Humanoid"]["WalkSpeedCheck"], float(val))
        self.memory.write_float(self.address + offsets["Humanoid"]["WalkSpeed"], float(val))

    @property
    def JumpPower(self):
        return self.memory.read_float(self.address + offsets["Humanoid"]["JumpPower"])
    
    @JumpPower.setter
    def JumpPower(self, val: float) -> None:
        self.memory.write_float(self.address + offsets["Humanoid"]["JumpPower"], float(val))
        self.memory.write_float(self.address + offsets["Humanoid"]["JumpHeight"], float(val))

    @property
    def HealthDisplayDistance(self):
        return int(self.memory.read_float(self.address + offsets["Humanoid"]["HealthDisplayDistance"]))
    
    @HealthDisplayDistance.setter
    def HealthDisplayDistance(self, val: float):
        return self.memory.write_float(self.address + offsets["Humanoid"]["HealthDisplayDistance"], float(val))
    
    @property
    def HealthDisplayType(self):
        return int(self.memory.read(self.address + offsets["Humanoid"]["HealthDisplayType"], 1)[0])

    @HealthDisplayType.setter
    def HealthDisplayType(self, val: int): 
        self.memory.write(self.address + offsets["Humanoid"]["HealthDisplayType"], val.to_bytes(1, byteorder="big"))

    @property
    def NameDisplayDistance(self):
        return int(self.memory.read_float(self.address + offsets["Humanoid"]["NameDisplayDistance"]))
    
    @property
    def HipHeight(self):
        return self.memory.read_float(self.address + offsets["Humanoid"]["HipHeight"])
    
    @HipHeight.setter
    def HipHeight(self, val: float):
        return self.memory.write_float(self.address + offsets["Humanoid"]["HipHeight"], float(val))
    
    @property
    def DisplayName(self):
        return self.memory.read_string(self.address + offsets["Player"]["DisplayName"])
    
    @DisplayName.setter
    def DisplayName(self, writer: str):
        print("warning: writing to displayname isnt recommended")
        return self.memory.write_string(self.address + offsets["Player"]["DisplayName"], writer)
    
    @property
    def UserId(self):
        return self.memory.read_ptr(self.address + offsets["Player"]["UserId"])
    
    @UserId.setter
    def UserId(self, val: int):
        print("warning: writing to UserId isnt recommended")
        return self.memory.write_int(self.address + offsets["Player"]["UserId"], val)
        
    @property
    def RigType(self):
        rig = memory.read(self.address + offsets["Humanoid"]["RigType"], 2)
        return struct.unpack('<H', rig)[0] 
        
    @RigType.setter
    def RigType(self, value):
        memory.write(self.address + offsets["Humanoid"]["RigType"], struct.pack('<H', value))

    @property
    def CFrame(self):
        primitive = memory.read_ptr(self.address + offsets["BasePart"]["Primitive"])
        raw = memory.read(primitive + offsets["Primitive"]["CFrame"], 48)
        print(raw)
        return CFrame.from_bytes(raw)
    
    @CFrame.setter
    def CFrame(self, value: CFrame):
        primitive = memory.read_ptr(self.address + offsets["BasePart"]["Primitive"])
        cf_addr = primitive + offsets["Primitive"]["CFrame"]

        if value.LookVector.x == 0 and value.LookVector.y == 0:
            raw = memory.read(cf_addr, 48)
            existing = list(struct.unpack('<12f', raw))
            existing[9] = float(value._x)
            existing[10] = float(value._y)
            existing[11] = float(value._z)
            packed = struct.pack('<12f', *existing)
        else:
            packed = value.to_bytes()

        for i in range(20):
            memory.write(cf_addr, packed)
    
    @property
    def Velocity(self): 
        return Vector3.from_bytes(memory.read(memory.read_ptr(self.address + offsets["BasePart"]["Primitive"]) + offsets["Primitive"]["AssemblyLinearVelocity"], 12))
    
    @Velocity.setter
    def Velocity(self, value: Vector3):
        memory.write(memory.read_ptr(self.address + offsets["BasePart"]["Primitive"]) + offsets["Primitive"]["AssemblyLinearVelocity"], value.to_bytes())

    @property
    def AngularVelocity(self): 
        return Vector3.from_bytes(memory.read(memory.read_ptr(self.address + offsets["BasePart"]["Primitive"]) + offsets["Primitive"]["AssemblyAngularVelocity"], 12))
    
    @AngularVelocity.setter
    def AngularVelocity(self, value: Vector3):
        memory.write(memory.read_ptr(self.address + offsets["BasePart"]["Primitive"]) + offsets["Primitive"]["AssemblyAngularVelocity"], value.to_bytes())


class DataModel:
    def __init__(self):
        self.cachedDm = 0

    def find(self):
        fakedm = memory.read_ptr(memory.get_base() + offsets["FakeDataModel"]["Pointer"],) 
        if not fakedm: print("idk i didnt find fake datamodel")

        realdm = memory.read_ptr(fakedm + offsets["FakeDataModel"]["RealDataModel"])
        print("datamodel is ->", hex(realdm))
        self.cachedDm = realdm
        
        return realdm
    
    def Workspace(self):
        if self.cachedDm == 0: self.find()
        return memory.read_ptr(self.cachedDm + offsets["DataModel"]["Workspace"])
    
    def get_mem(self):
        return memory