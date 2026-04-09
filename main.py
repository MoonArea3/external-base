from roblox.world import *
import struct, re

dm = DataModel()
ptr = dm.find()
game = Instance(ptr)
memory = dm.get_mem()

players = game.FindFirstChild("Players")
workspace = game.FindFirstChild("Workspace")

"""
now have fun
# here is how to find a character!
players.FindFirstChild("MoonArea3").Character
humanoid
players.FindFirstChild("MoonArea3").Character.Humanoid
"""
