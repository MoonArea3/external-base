from roblox.world import *
import struct, re

dm = DataModel()
ptr = dm.find()
datamodel = Instance(ptr)
memory = dm.get_mem()

terrain = datamodel.FindFirstChild("Workspace").FindFirstChild("Terrain").Address
# unfinished