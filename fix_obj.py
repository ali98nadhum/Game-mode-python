import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the OBJ generation in app.py to have clockwise winding order
old_obj_gen = """                box_obj = f"mtllib item{item_index}.mtl\\n"
                box_obj += "v -0.5 -0.5 0.5\\nv 0.5 -0.5 0.5\\nv 0.5 0.5 0.5\\nv -0.5 0.5 0.5\\n"
                box_obj += "v -0.5 -0.5 -0.5\\nv 0.5 -0.5 -0.5\\nv 0.5 0.5 -0.5\\nv -0.5 0.5 -0.5\\n"
                box_obj += "vt 0.543 0.0\\nvt 1.0 0.0\\nvt 1.0 1.0\\nvt 0.543 1.0\\n" # Front (1-4)
                box_obj += "vt 0.457 0.0\\nvt 0.0 0.0\\nvt 0.0 1.0\\nvt 0.457 1.0\\n" # Back (5-8)
                box_obj += "vt 0.457 0.0\\nvt 0.543 0.0\\nvt 0.543 1.0\\nvt 0.457 1.0\\n" # Spine/Sides (9-12)
                box_obj += "usemtl Material\\n"
                box_obj += "f 1/1 2/2 3/3 4/4\\n" # Front
                box_obj += "f 6/5 5/6 8/7 7/8\\n" # Back
                box_obj += "f 5/9 1/10 4/11 8/12\\n" # Left
                box_obj += "f 2/9 6/10 7/11 3/12\\n" # Right
                box_obj += "f 4/9 3/10 7/11 8/12\\n" # Top
                box_obj += "f 5/9 6/10 2/11 1/12\\n" # Bottom"""

# Reversing vertex order for each face to fix winding
new_obj_gen = """                box_obj = f"mtllib item{item_index}.mtl\\n"
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

content = content.replace(old_obj_gen, new_obj_gen)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

