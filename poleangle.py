bl_info = {
    "name": "Poleangle",
    "author": "Likkez",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "description": "Calculate pole angle for IK constraint",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}


import bpy
from mathutils import *
from math import radians



#credits: https://blender.stackexchange.com/questions/3452/is-it-possible-to-add-a-button-to-an-existing-panel-or-node-with-python/3453

#This only edits pole angle for first constraint on the list because I'm dumb. Still, why would you have more than one?



def signed_angle(vector_u, vector_v, normal):
    # Normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle
    return angle

def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)

def find_constraint(bone):
    for c in bone.constraints:
        if c.type=='IK':
            return c


class PA_OT_poleangle(bpy.types.Operator):
    bl_description = "Calculate Pole angle."
    bl_idname = 'constraint.ik_poleangle'
    bl_label = "Calculate Pole Angle"
    bl_options = set({'REGISTER', 'UNDO'}) 
    
    
    def execute(self, context):
        ik_bone = bpy.context.active_pose_bone        
        arm = ik_bone.id_data


        constraint = find_constraint(ik_bone)
        if not constraint:
            return {'CANCELLED'}

        arm_mute = arm.data.pose_position

        if constraint.pole_subtarget:
            pole_bone = arm.pose.bones[constraint.pole_subtarget]
        else:
            return {'CANCELLED'}

        base_bone = ik_bone.parent


        arm.data.pose_position = 'REST'
        bpy.context.view_layer.update()


        pole_angle_in_radians = get_pole_angle(base_bone,
                                               ik_bone,
                                               pole_bone.matrix.translation)
        pole_angle_in_deg = round(180*pole_angle_in_radians/3.141592, 3)


        print(pole_angle_in_deg)
        constraint.pole_angle = radians(pole_angle_in_deg)


        arm.data.pose_position = arm_mute
        return {'FINISHED'}


def poleangle_panel(self, context):
    layout = self.layout
    con = self.get_constraint(context)

    if con.target and con.subtarget and con.pole_target and con.pole_subtarget:    
        col = layout.column(align = True)
        col.operator('constraint.ik_poleangle', text="Calculate Pole Angle")

# Registration

def register():
    from bpy.utils import register_class
    register_class(PA_OT_poleangle)
    bpy.types.BONE_PT_bKinematicConstraint.append(poleangle_panel)

# Unregistration

def unregister():
    from bpy.utils import unregister_class
    unregister_class(PA_OT_poleangle)
    bpy.types.BONE_PT_bKinematicConstraint.remove(poleangle_panel)