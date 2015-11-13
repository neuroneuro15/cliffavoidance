from psychopy import event
import motive
import ratcave as rc
import numpy as np

from os import path

import warnings

np.set_printoptions(precision=2, suppress=True)

resource_path = 'Objects'

# Load Motive file and Set Rigid Bodies to Track
motive.load_project("vr_demo.ttp")
motive.update()
rat_rb = motive.get_rigid_bodies()['CalibWand']
arena_rb = motive.get_rigid_bodies()['Arena']

# Realign everything to the arena, for proper positioning
for attempt in range(4):
    arena_rb.reset_orientation()
    motive.update()
    if arena_rb.rotation_global[1] < .2:
        break
else:
    raise AssertionError("Couldn't reset orientation properly after 4 tries.\nCurrent Rotation: {}".format(arena_rb.rotation_global))

arena_markers = np.array(arena_rb.point_cloud_markers)
additional_rotation = rc.utils.rotate_to_var(arena_markers)

# Create Arena
arena_reader = rc.graphics.WavefrontReader(rc.graphics.resources.obj_arena)
arena = arena_reader.get_mesh('Arena', lighting=True, centered=False)

# Import Cliff Avoidance objects
reader = rc.graphics.WavefrontReader(path.join(resource_path, 'CliffAvoidance.obj'))
walls = reader.get_mesh('FakeArena')
board = reader.get_mesh('Board')
floor_left = reader.get_mesh('DepthLeft')
floor_right= reader.get_mesh('DepthRight')

floor_right.local.position[1] -= 2.

meshes = [walls, board, floor_left, floor_right]

# Put an image texture on the walls and floors
for mesh in [walls, floor_left, floor_right]:
    mesh.load_texture(path.join(resource_path, 'uvgrid.png'))



for mesh in meshes + [arena]:
    mesh.world.position = arena_rb.location
    mesh.world.rotation = arena_rb.rotation_global
    mesh.world.rotation[1] += additional_rotation


# Build ratCAVE Scenes
active_scene = rc.graphics.Scene([arena, board])
active_scene.bgColor.rgb = 0., .3, 0.
active_scene.camera = rc.graphics.projector
active_scene.camera.fov_y = 27.8
active_scene.light.position = active_scene.camera.position
arena.cubemap = True

virtual_scene = rc.graphics.Scene(meshes)
virtual_scene.light.position = active_scene.camera.position
virtual_scene.light.rotation = active_scene.camera.rotation
virtual_scene.bgColor.rgb = .1, 0., .1
#virtual_scene.camera.zFar = 4.


# Build ratCAVE Window
window = rc.graphics.Window(active_scene, screen=1, fullscr=True,
                            virtual_scene=virtual_scene,
                            shadow_rendering=False)


# Draw update function
def graphics_update():
    motive.update()
    virtual_scene.camera.position = rat_rb.location
    window.draw()
    window.flip()


# Set Floor Height
warnings.warn("NotImplementedWarning: Floors are currently set at default height!")

# Save Data
warnings.warn("NotImplementedWarning: No data is being saved yet!  Don't use for production!")

# Main Experiment Loop
while 'escape' not in event.getKeys():
    graphics_update()