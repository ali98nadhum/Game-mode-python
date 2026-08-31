import os
import json
import urllib.request
import shutil
import re
from PIL import Image, ImageFilter
from src.utils.helpers import TEMPLATES_DIR

class ItemProcessor:
    @staticmethod
    def process_item_addition(pack_path, title, image_source, price, template_name, use_smart_process, shape_choice):
        # We need to map shape_choice strings back to the exact strings from the UI if we aren't using the ar() wrapped ones.
        # But wait, in the backend we can just pass the shape_choice directly and compare against the raw text before `ar()` or pass a shape_id.
        # For simplicity, we'll assume shape_choice is passed in as raw Arabic text (or an Enum) so we can compare it properly.
        # Let's map it from raw Arabic to avoid issues.
        
        json_path = os.path.join(pack_path, "products.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"تعذرت قراءة ملف products.json: {e}")
            
        license_data = data["ProductLicenses"][0]
        products = license_data["Products"]
        
        item_index = len(products) + 1
        base_id = license_data["ID"]
        next_id = products[-1]["ID"] + 1 if products else base_id + 1
        
        temp_img = os.path.join(pack_path, "temp_img.jpg")
        
        try:
            # 1. Fetch Template info
            template_dir = os.path.join(TEMPLATES_DIR, template_name)
            template_obj = os.path.join(template_dir, "template.obj")
            template_mtl = os.path.join(template_dir, "template.mtl")
            
            template_img_path = None
            for ext in ["jpg", "jpeg", "png", "webp"]:
                p = os.path.join(template_dir, f"template.{ext}")
                if os.path.exists(p):
                    template_img_path = p
                    break
                    
            if not os.path.exists(template_obj) or not os.path.exists(template_mtl):
                raise ValueError("قوالب الـ 3D مفقودة من هذا المجلد! يرجى إضافة المجسمات أولاً.")
                
            tex_w, tex_h = 3173, 1962 # default fallback
            if template_img_path:
                with Image.open(template_img_path) as t_img:
                    tex_w, tex_h = t_img.size

            # 2. Fetch User Image
            if image_source.startswith("http://") or image_source.startswith("https://"):
                req = urllib.request.Request(image_source, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(temp_img, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            else:
                shutil.copy(image_source, temp_img)
                
            img = Image.open(temp_img).convert("RGB")
            
            icon_path = os.path.join(pack_path, "products_icons", f"item{item_index}.png") # Saving icons as PNG is better
            tex_path = os.path.join(pack_path, "objects_textures", f"item{item_index}.png") # Textures as PNG
            
            # Using LANCZOS (Pillow 10+)
            icon = img.resize((1519, 1750), Image.Resampling.LANCZOS)
            icon.save(icon_path)
            
            # 3. Image Processing Logic
            if use_smart_process:
                is_game = any(word in template_name.lower() for word in ["game", "blu-ray", "manga"])
                # Shape choices
                shape_std = "حجم قياسي (PS4/PS5/Blu-ray)"
                shape_square = "مربع وسميك (PS1/CD)"
                shape_switch = "نحيف وطويل (Nintendo Switch)"
                shape_keyboard = "مستطيل عريض (Keyboard)"
                shape_phone = "علبة هاتف (Mobile Phone)"
                shape_console = "كرتون كونسول ضخم (PS4/Xbox)"
                
                is_custom_box = shape_choice != shape_std
                
                if is_game or is_custom_box:
                    composite = Image.new('RGB', (3173, 1962), color=(15, 20, 35))
                    front_w, spine_w, back_w = 1450, 273, 1450
                    
                    aspect_ratio = img.width / img.height
                    
                    if aspect_ratio > 1.2 and not is_custom_box:
                        # FULL COVER PROVIDED (Auto-Crop)
                        if shape_choice == shape_square:
                            expected_front_ratio = 1.0
                        elif shape_choice == shape_switch:
                            expected_front_ratio = 0.6
                        else:
                            expected_front_ratio = 0.739 # Standard
                            
                        actual_front_w = int(img.height * expected_front_ratio)
                        
                        if actual_front_w * 2 >= img.width:
                            actual_front_w = int(img.width * 0.45)
                            
                        back_part = img.crop((0, 0, actual_front_w, img.height))
                        front_part = img.crop((img.width - actual_front_w, 0, img.width, img.height))
                        spine_part = img.crop((actual_front_w, 0, img.width - actual_front_w, img.height))
                        
                        composite.paste(back_part.resize((back_w, 1962), Image.Resampling.LANCZOS), (0, 0))
                        composite.paste(spine_part.resize((spine_w, 1962), Image.Resampling.LANCZOS), (back_w, 0))
                        composite.paste(front_part.resize((front_w, 1962), Image.Resampling.LANCZOS), (back_w + spine_w, 0))
                    else:
                        # FRONT COVER ONLY (Generate spine and blurred back)
                        front_cover = img.resize((front_w, 1962), Image.Resampling.LANCZOS)
                        composite.paste(front_cover, (back_w + spine_w, 0))
                        
                        back_cover = img.resize((back_w, 1962), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
                        darkener = Image.new('RGB', (back_w, 1962), color=(0, 0, 0))
                        back_cover = Image.blend(back_cover, darkener, alpha=0.5)
                        composite.paste(back_cover, (0, 0))
                        
                        spine_cover = img.resize((spine_w, 1962), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(15))
                        spine_cover = Image.blend(spine_cover, Image.new('RGB', (spine_w, 1962), color=(0, 0, 0)), alpha=0.2)
                        composite.paste(spine_cover, (back_w, 0))
                    
                    final_texture = composite.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
                    final_texture.save(tex_path)
                else:
                    bg = img.resize((tex_w, tex_h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(50))
                    darkener = Image.new('RGB', (tex_w, tex_h), color=(0, 0, 0))
                    bg = Image.blend(bg, darkener, alpha=0.4)
                    
                    fg_h = int(tex_h * 0.45)
                    fg_w = int(img.width * (fg_h / img.height))
                    fg = img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
                    
                    bg.paste(fg, ((tex_w - fg_w) // 2, (tex_h - fg_h) // 2))
                    
                    logo_h = int(tex_h * 0.2)
                    logo_w = int(img.width * (logo_h / img.height))
                    logo = img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                    
                    margin_x = int(tex_w * 0.05)
                    margin_y = int(tex_h * 0.05)
                    
                    bg.paste(logo, (margin_x, margin_y))
                    bg.paste(logo, (tex_w - logo_w - margin_x, margin_y))
                    bg.paste(logo, (margin_x, tex_h - logo_h - margin_y))
                    bg.paste(logo, (tex_w - logo_w - margin_x, tex_h - logo_h - margin_y))
                    
                    final_texture = bg
                    final_texture.save(tex_path)
            else:
                final_texture = img.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
                
            # Fix Unity mapping issues
            if template_name == "Blu-ray":
                # The Blu-ray template .obj in Unity displays the texture rotated 90 degrees to the right.
                # We rotate it 90 degrees counter-clockwise (ROTATE_90) to compensate.
                final_texture = final_texture.transpose(Image.ROTATE_90)
            elif is_custom_box:
                # For custom shapes we generate, we just need to match Unity's V=0 at bottom standard
                final_texture = final_texture.transpose(Image.FLIP_TOP_BOTTOM)
                
            final_texture.save(tex_path)
                
            # 4. Copy 3D Models
            new_obj = os.path.join(pack_path, "objects_meshes", f"item{item_index}.obj")
            new_mtl = os.path.join(pack_path, "objects_meshes", f"item{item_index}.mtl")
            
            if is_custom_box:
                # Generate a unit cube with pivot at bottom center (Y: 0 to 1)
                box_obj = f"mtllib item{item_index}.mtl\n"
                # Vertices: 1-4 Front, 5-8 Back (Y changed from -0.5,0.5 to 0.0,1.0)
                box_obj += "v -0.5 0.0 0.5\nv 0.5 0.0 0.5\nv 0.5 1.0 0.5\nv -0.5 1.0 0.5\n"
                box_obj += "v -0.5 0.0 -0.5\nv 0.5 0.0 -0.5\nv 0.5 1.0 -0.5\nv -0.5 1.0 -0.5\n"
                # Normals
                box_obj += "vn 0 0 1\nvn 0 0 -1\nvn -1 0 0\nvn 1 0 0\nvn 0 1 0\nvn 0 -1 0\n"
                
                # Standard Unity UVs (V=0 is bottom)
                box_obj += "vt 0.543 0.0\nvt 1.0 0.0\nvt 1.0 1.0\nvt 0.543 1.0\n" # Front 
                box_obj += "vt 0.457 0.0\nvt 0.0 0.0\nvt 0.0 1.0\nvt 0.457 1.0\n" # Back
                box_obj += "vt 0.457 0.0\nvt 0.543 0.0\nvt 0.543 1.0\nvt 0.457 1.0\n" # Spine/Sides
                
                box_obj += "usemtl Material\n"
                # Front face (+Z)
                box_obj += "f 1/1/1 4/4/1 3/3/1 2/2/1\n"
                # Back face (-Z)
                box_obj += "f 6/5/2 7/8/2 8/7/2 5/6/2\n"
                # Left face (-X)
                box_obj += "f 5/9/3 8/12/3 4/11/3 1/10/3\n"
                # Right face (+X)
                box_obj += "f 2/9/4 3/12/4 7/11/4 6/10/4\n"
                # Top face (+Y)
                box_obj += "f 4/9/5 8/12/5 7/11/5 3/10/5\n"
                # Bottom face (-Y)
                box_obj += "f 5/9/6 1/12/6 2/11/6 6/10/6\n" 
                
                with open(new_obj, "w") as f:
                    f.write(box_obj)
                    
                box_mtl = "newmtl Material\n"
                box_mtl += "Ka 1.000 1.000 1.000\nKd 1.000 1.000 1.000\nKs 0.000 0.000 0.000\n"
                box_mtl += f"map_Kd ../objects_textures/item{item_index}.png\n"
                with open(new_mtl, "w") as f:
                    f.write(box_mtl)
            else:
                with open(template_obj, "r") as f:
                    obj_content = f.read()
                obj_content = re.sub(r'mtllib\s+.*\.mtl', f'mtllib item{item_index}.mtl', obj_content)
                with open(new_obj, "w") as f:
                    f.write(obj_content)
                    
                with open(template_mtl, "r") as f:
                    mtl_content = f.read()
                mtl_content = re.sub(r'map_Kd\s+.*', f'map_Kd ../objects_textures/item{item_index}.png', mtl_content)
                with open(new_mtl, "w") as f:
                    f.write(mtl_content)
                
            # 5. Determine Box Shape Scale (meters)
            if shape_choice == shape_square:
                local_scale = [0.15, 0.15, 0.02]
            elif shape_choice == shape_switch:
                local_scale = [0.10, 0.17, 0.015]
            elif shape_choice == shape_keyboard:
                local_scale = [0.45, 0.15, 0.05]
            elif shape_choice == shape_phone:
                local_scale = [0.08, 0.16, 0.04]
            elif shape_choice == shape_console:
                local_scale = [0.40, 0.30, 0.15]
            else:
                local_scale = [1.2, 1.2, 1.2]
                
            is_console = (shape_choice == shape_console) or ("ps" in template_name.lower()) or ("xbox" in template_name.lower()) or ("console" in template_name.lower())
            
            if is_console:
                grid_in_box = {
                  "boxSize": "_20x20x20",
                  "productCount": 6,
                  "firstObjectPosition": [0.05, 0.32, -0.25],
                  "productAngles": [0.0, 0.0, 0.0],
                  "spacing": [0.17, 0.04, 0.10],
                  "productPlacement": [1,6],
                  "scaleMultiplier": 0.65
                }
                grid_in_storage = {
                  "boxSize": "_20x20x10",
                  "productCount": 3,
                  "firstObjectPosition": [0.0, 0.08, -0.18],
                  "productAngles": [0.0, 180.0, 0.0],
                  "spacing": [0.9, 0.9, 0.145],
                  "productPlacement": [1,3],
                  "scaleMultiplier": 1.0
                }
                item_grid_size = [2, 1]
                product_amount_on_purchase = 6
            else:
                grid_in_box = {
                    "boxSize": "_20x10x7",
                    "productCount": 20,
                    "firstObjectPosition": [0.27, -0.01, 0.0],
                    "productAngles": [0.0, 90.0, 0.0],
                    "spacing": [0.028, 0.0, 0.0],
                    "productPlacement": [20,1],
                    "scaleMultiplier": 1.0
                }
                grid_in_storage = {
                    "boxSize": "_20x10x7",
                    "productCount": 60,
                    "firstObjectPosition": [0.31, 0.01, -0.21],
                    "productAngles": [0.0, 0.0, 0.0],
                    "spacing": [0.21, 0.0, 0.027],
                    "productPlacement": [4,15],
                    "scaleMultiplier": 1.1
                }
                item_grid_size = [2, 1]
                product_amount_on_purchase = 20
                
            # 6. Update JSON
            new_product = {
                "ID": next_id,
                "ProductName": title,
                "ProductBrand": "ModMaker",
                "ProductIcon": f"products_icons/item{item_index}.png",
                "BoxIcon": f"products_icons/item{item_index}.png",
                "ProductDisplayType": "SHELF",
                "Category": "EDIBLE",
                "ProductPrefab": {
                    "objPath": f"objects_meshes/item{item_index}.obj",
                    "mtlPath": f"objects_meshes/item{item_index}.mtl",
                    "localScale": local_scale
                },
                "ProductAmountOnPurchase": product_amount_on_purchase,
                "BasePrice": price,
                "MinDynamicPrice": round(price * 0.8, 2),
                "MaxDynamicPrice": round(price * 1.5, 2),
                "OptimumProfitRate": 100.0,
                "MaxProfitRate": 120.0,
                "GridLayoutInBox": grid_in_box,
                "GridLayoutInStorage": grid_in_storage,
                "ItemGridSize": item_grid_size
            }
            
            products.append(new_product)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            if os.path.exists(temp_img):
                os.remove(temp_img)
                
        except Exception as e:
            raise ValueError(f"فشلت عملية الإضافة: {e}")
