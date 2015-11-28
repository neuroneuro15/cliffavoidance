import natnetclient
import ratcave as rc
import numpy as np
import cliff_utills

from os import path
from psychopy import event

# Parameters
floor_depth = 1.5

# Connect to Motive and Set Rigid Bodies to Track
tracker = natnetclient.NatClient()
rat_rb = tracker.rigid_bodies['CalibWand']
arena_rb = tracker.rigid_bodies['Arena']

# Realign everything to the arena, for proper positioning
additional_rotation = rc.utils.correct_orientation_natnet(arena_rb)

# Create Arena
arena_reader = rc.graphics.WavefrontReader(rc.graphics.resources.obj_arena)
arena = arena_reader.get_mesh('Arena', lighting=True, centered=False)

# Import Cliff Avoidance objects
reader = rc.graphics.WavefrontReader(path.join('Objects', 'CliffAvoidance.obj'))
walls = reader.get_mesh('FakeArena')
board = reader.get_mesh('Board')
floor_left = reader.get_mesh('DepthLeft')
floor_right= reader.get_mesh('DepthRight')

# Use a Pseudo-Random order for determining which side the deep floor should be on.
side_bool = cliff_utills.read_and_pop_pickle_list('side_order_list.pickle')
floor_to_change = floor_right if side_bool else floor_left
floor_to_change.local.y -= floor_depth

meshes = [walls, board, floor_left, floor_right]#, points]

# Put an image texture on the walls and floors
for mesh in [walls, floor_left, floor_right]:
    mesh.load_texture(rc.graphics.resources.img_uvgrid)


rc.utils.update_world_position_natnet(meshes + [arena], arena_rb, additional_rotation)


# Build ratCAVE Scenes
active_scene = rc.graphics.Scene([arena, board])
active_scene.bgColor.rgb = 0., .3, 0.
active_scene.camera = rc.graphics.projector
active_scene.camera.fov_y = 27.8
active_scene.light.position = active_scene.camera.position
active_scene.light.rotation = active_scene.camera.rotation
arena.cubemap = True

virtual_scene = rc.graphics.Scene(meshes)
virtual_scene.light.position = active_scene.camera.position
virtual_scene.light.rotation = active_scene.camera.rotation
virtual_scene.bgColor.rgb = .1, 0., .1
#virtual_scene.camera.zFar = 4.


# Build ratCAVE Window
window = rc.graphics.Window(active_scene, screen=1, fullscr=True, virtual_scene=virtual_scene, shadow_rendering=False)


# Save Data
print('Please start Motive recording before continuing!')
while not tracker.is_recording:
    pass

# Main Experiment Loop
while 'escape' not in event.getKeys():
    virtual_scene.camera.position = rat_rb.position
    window.draw()
    window.flip()