import os
import json
import re
from PIL import Image
from src.utils.helpers import TEMPLATES_DIR

class ItemProcessor:
    
    @staticmethod
    def process_item_addition(pack_path, title, image_source, price, template_name, use_smart_process, shape_choice):
        """
        Process the image and 3D files to add a new item to the pack.
        We strictly use the template's .obj and .mtl, and resize the image to match the template's texture.
        """
        json_path = os.path.join(pack_path, "products.json")
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            raise ValueError("ملف products.json غير موجود، تأكد من إنشاء الحزمة أولاً.")
            
        products = data.get("Products", [])
        base_id = data.get("LicenseInfo", {}).get("BaseID", 98000)
        item_index = len(products)
        next_id = base_id + item_index
        
        template_dir = os.path.join(TEMPLATES_DIR, template_name)
        if not os.path.exists(template_dir):
            raise ValueError(f"مجلد القالب غير موجود: {template_name}")
            
        template_obj = os.path.join(template_dir, "template.obj")
        template_mtl = os.path.join(template_dir, "template.mtl")
        
        if not os.path.exists(template_obj) or not os.path.exists(template_mtl):
            raise ValueError(f"ملفات القالب الأساسية (.obj / .mtl) مفقودة في المجلد: {template_name}")

        # Determine the target texture size from the template's reference texture if it exists
        # We look for template.png or template.jpg
        target_size = (1024, 1024) # Fallback
        template_tex = os.path.join(template_dir, "template.png")
        if not os.path.exists(template_tex):
            template_tex = os.path.join(template_dir, "template.jpg")
            
        if os.path.exists(template_tex):
            try:
                with Image.open(template_tex) as t_img:
                    target_size = t_img.size
            except Exception:
                pass
        elif template_name == "Blu-ray":
            target_size = (1024, 804)
        elif template_name == "Console":
            target_size = (857, 1251)

        try:
            # 1. Process Icon
            icon_path = os.path.join(pack_path, "products_icons", f"item{item_index}.png")
            img = Image.open(image_source).convert("RGBA")
            
            icon = img.resize((256, 256), Image.Resampling.LANCZOS)
            icon.save(icon_path)
            
            # 2. Process Texture
            tex_path = os.path.join(pack_path, "objects_textures", f"item{item_index}.png")
            
            tex_w, tex_h = target_size
            
            # If user wants Smart Processing for Blu-ray games (generating full spread from front cover)
            if use_smart_process and template_name == "Blu-ray":
                aspect_ratio = img.height / img.width
                if aspect_ratio > 1.2:  # It's a front cover
                    # Crop logic for 1024x804 Blu-ray
                    actual_front_w = int(img.width * 0.95)
                    back_part = img.crop((0, 0, actual_front_w, img.height))
                    front_part = img.crop((img.width - actual_front_w, 0, img.width, img.height))
                    spine_part = img.crop((actual_front_w, 0, img.width - actual_front_w, img.height))
                    
                    composite = Image.new("RGBA", (tex_w, tex_h), (255, 255, 255, 255))
                    back_w, spine_w, front_w = 492, 40, 492
                    
                    composite.paste(back_part.resize((back_w, tex_h), Image.Resampling.LANCZOS), (0, 0))
                    composite.paste(spine_part.resize((spine_w, tex_h), Image.Resampling.LANCZOS), (back_w, 0))
                    composite.paste(front_part.resize((front_w, tex_h), Image.Resampling.LANCZOS), (back_w + spine_w, 0))
                    
                    # PlayStation / PS5 Header Logic
                    try:
                        logo = Image.open(os.path.join(TEMPLATES_DIR, "ps5_header.png")).convert("RGBA")
                        header_h = int(tex_h * 0.12)
                        logo = logo.resize((tex_w, header_h), Image.Resampling.LANCZOS)
                        composite.paste(logo, (0, 0), logo)
                    except Exception:
                        pass
                        
                    final_texture = composite
                else:
                    # It's already a full spread
                    final_texture = img.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
            else:
                # Direct resize to match template exactly!
                final_texture = img.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
                
            # DO NOT rotate or flip. The user provides the correct texture layout, or we use the proven smart process.
            final_texture.save(tex_path)
                
            # 3. Copy 3D Models Exactly as they are in the template
            new_obj = os.path.join(pack_path, "objects_meshes", f"item{item_index}.obj")
            new_mtl = os.path.join(pack_path, "objects_meshes", f"item{item_index}.mtl")
            
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
                
            # 4. JSON Grid Logic depending on whether it's a console or normal box
            is_console = template_name.lower() == "console"
            
            if is_console:
                local_scale = [0.40, 0.30, 0.15]
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
                # Default for Blu-ray and all other custom templates
                local_scale = [1.2, 1.2, 1.2]
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
                
            # 5. Update JSON
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
                
        except Exception as e:
            raise ValueError(f"فشلت عملية الإضافة: {e}")
