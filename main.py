from roblox.world import *
import struct, re

dm = DataModel()
ptr = dm.find()
game = Instance(ptr)
memory = dm.get_mem()

players = game.Players
workspace = game.Workspace

"""
now have fun
# here is how to find a character!
game.Players.MoonArea3.Character
humanoid
game.Players.MoonArea3.Character.Humanoid
"""
