import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the Auto-Crop (Chopped) logic
old_crop = """                    if aspect_ratio > 1.2:
                        # FULL COVER PROVIDED (Auto-Crop)"""
new_crop = """                    if aspect_ratio > 1.2 and not is_custom_box:
                        # FULL COVER PROVIDED (Auto-Crop)"""
content = content.replace(old_crop, new_crop)

# 2. Fix the Box OBJ (Pivot at bottom, check UVs for inverted)
old_obj_gen = """                # Generate a unit cube with proper UVs
                box_obj = f"mtllib item{item_index}.mtl\\n"
                box_obj += "v -0.5 -0.5 0.5\\nv 0.5 -0.5 0.5\\nv 0.5 0.5 0.5\\nv -0.5 0.5 0.5\\n"
                box_obj += "v -0.5 -0.5 -0.5\\nv 0.5 -0.5 -0.5\\nv 0.5 0.5 -0.5\\nv -0.5 0.5 -0.5\\n"
                # Add Normals for Unity (just in case)
                box_obj += "vn 0 0 1\\nvn 0 0 -1\\nvn -1 0 0\\nvn 1 0 0\\nvn 0 1 0\\nvn 0 -1 0\\n"
                box_obj += "vt 0.543 0.0\\nvt 1.0 0.0\\nvt 1.0 1.0\\nvt 0.543 1.0\\n" # Front (1-4)
                box_obj += "vt 0.457 0.0\\nvt 0.0 0.0\\nvt 0.0 1.0\\nvt 0.457 1.0\\n" # Back (5-8)
                box_obj += "vt 0.457 0.0\\nvt 0.543 0.0\\nvt 0.543 1.0\\nvt 0.457 1.0\\n" # Spine/Sides (9-12)
                box_obj += "usemtl Material\\n"
                # Front face (+Z)
                box_obj += "f 1/1/1 4/4/1 3/3/1 2/2/1\\n"
                # Back face (-Z)
                box_obj += "f 6/5/2 7/8/2 8/7/2 5/6/2\\n"
                # Left face (-X)
                box_obj += "f 5/9/3 8/12/3 4/11/3 1/10/3\\n"
                # Right face (+X)
                box_obj += "f 2/9/4 3/12/4 7/11/4 6/10/4\\n"
                # Top face (+Y)
                box_obj += "f 4/9/5 8/12/5 7/11/5 3/10/5\\n"
                # Bottom face (-Y)
                box_obj += "f 5/9/6 1/12/6 2/11/6 6/10/6\\n" """

new_obj_gen = """                # Generate a unit cube with pivot at bottom center (Y: 0 to 1)
                box_obj = f"mtllib item{item_index}.mtl\\n"
                # Vertices: 1-4 Front, 5-8 Back (Y changed from -0.5,0.5 to 0.0,1.0)
                box_obj += "v -0.5 0.0 0.5\\nv 0.5 0.0 0.5\\nv 0.5 1.0 0.5\\nv -0.5 1.0 0.5\\n"
                box_obj += "v -0.5 0.0 -0.5\\nv 0.5 0.0 -0.5\\nv 0.5 1.0 -0.5\\nv -0.5 1.0 -0.5\\n"
                # Normals
                box_obj += "vn 0 0 1\\nvn 0 0 -1\\nvn -1 0 0\\nvn 1 0 0\\nvn 0 1 0\\nvn 0 -1 0\\n"
                
                # If image is upside down in Unity, we might need to invert V (1.0 - V). 
                # Let's invert V because Unity reads textures from bottom-up, but PIL saves top-down.
                # Actually, standard is V=0 is bottom. Let's swap 0 and 1 for V.
                # Front (1-4) BL, BR, TR, TL -> mapped to TopLeft to BottomRight if V is inverted?
                # Let's map it normally but flipped vertically: V=1.0 is bottom, V=0.0 is top.
                box_obj += "vt 0.543 1.0\\nvt 1.0 1.0\\nvt 1.0 0.0\\nvt 0.543 0.0\\n" # Front 
                box_obj += "vt 0.457 1.0\\nvt 0.0 1.0\\nvt 0.0 0.0\\nvt 0.457 0.0\\n" # Back
                box_obj += "vt 0.457 1.0\\nvt 0.543 1.0\\nvt 0.543 0.0\\nvt 0.457 0.0\\n" # Spine/Sides
                
                box_obj += "usemtl Material\\n"
                # Front face (+Z)
                box_obj += "f 1/1/1 4/4/1 3/3/1 2/2/1\\n"
                # Back face (-Z)
                box_obj += "f 6/5/2 7/8/2 8/7/2 5/6/2\\n"
                # Left face (-X)
                box_obj += "f 5/9/3 8/12/3 4/11/3 1/10/3\\n"
                # Right face (+X)
                box_obj += "f 2/9/4 3/12/4 7/11/4 6/10/4\\n"
                # Top face (+Y)
                box_obj += "f 4/9/5 8/12/5 7/11/5 3/10/5\\n"
                # Bottom face (-Y)
                box_obj += "f 5/9/6 1/12/6 2/11/6 6/10/6\\n" """

content = content.replace(old_obj_gen, new_obj_gen)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
