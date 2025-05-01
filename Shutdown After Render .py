bl_info = {
    "name": "Shutdown After Render",
    "blender": (2, 80, 0),
    "category": "Render",
    "author": "ChatGPT + @zorinel",
    "description": "Render image or animation and optionally shut down the computer after completion."
}

import bpy
import os
import platform
import subprocess

# Scene properties
def init_props():
    bpy.types.Scene.shutdown_after_render = bpy.props.BoolProperty(
        name="Shutdown After Render",
        default=False,
        description="Automatically shut down the computer after rendering finishes"
    )
    bpy.types.Scene.render_type = bpy.props.EnumProperty(
        name="Render Type",
        items=[
            ('IMAGE', "Image", "Render a still image"),
            ('ANIMATION', "Animation", "Render an animation")
        ],
        default='IMAGE'
    )
    bpy.types.Scene.output_folder = bpy.props.StringProperty(
        name="Output Folder",
        subtype='DIR_PATH',
        default="//",
        description="Folder to save rendered files"
    )

def clear_props():
    del bpy.types.Scene.shutdown_after_render
    del bpy.types.Scene.render_type
    del bpy.types.Scene.output_folder

# Shutdown logic
def shutdown_system():
    system = platform.system()
    if system == "Windows":
        subprocess.call(["shutdown", "/s", "/t", "60"])
    elif system == "Linux" or system == "Darwin":
        os.system("shutdown -h +1")
    else:
        print("Unknown OS, shutdown not supported.")

def cancel_shutdown():
    system = platform.system()
    if system == "Windows":
        subprocess.call(["shutdown", "/a"])
    elif system == "Linux" or system == "Darwin":
        os.system("shutdown -c")
    else:
        print("Unknown OS, cannot cancel shutdown.")

# Render complete handler
def render_complete_handler(scene):
    if scene.shutdown_after_render:
        print("Render complete. Shutdown scheduled.")
        shutdown_system()

# Operator: start render
class SHUTDOWN_OT_StartRender(bpy.types.Operator):
    bl_idname = "shutdown.start_render"
    bl_label = "Start Render"

    def execute(self, context):
        scene = context.scene
        output_path = bpy.path.abspath(scene.output_folder)
        scene.render.filepath = output_path

        if scene.render_type == 'IMAGE':
            bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
        else:
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

        return {'FINISHED'}

# Operator: cancel shutdown
class SHUTDOWN_OT_CancelShutdown(bpy.types.Operator):
    bl_idname = "shutdown.cancel_shutdown"
    bl_label = "Cancel Shutdown"

    def execute(self, context):
        cancel_shutdown()
        self.report({'INFO'}, "Shutdown canceled.")
        return {'FINISHED'}

# UI Panel
class SHUTDOWN_PT_Panel(bpy.types.Panel):
    bl_label = "Shutdown After Render"
    bl_idname = "SHUTDOWN_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "render_type")
        layout.prop(scene, "output_folder")
        layout.operator("shutdown.start_render", icon='RENDER_STILL' if scene.render_type == 'IMAGE' else 'RENDER_ANIMATION')
        layout.prop(scene, "shutdown_after_render")
        layout.separator()
        layout.operator("shutdown.cancel_shutdown", icon='CANCEL')

# Registration
classes = (
    SHUTDOWN_PT_Panel,
    SHUTDOWN_OT_StartRender,
    SHUTDOWN_OT_CancelShutdown,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    init_props()
    if render_complete_handler not in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.append(render_complete_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if render_complete_handler in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(render_complete_handler)
    clear_props()

if __name__ == "__main__":
    register()
