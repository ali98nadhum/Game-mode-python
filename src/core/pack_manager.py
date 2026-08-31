import os
import json
from src.utils.helpers import PACKS_DIR, TEMPLATES_DIR

class PackManager:
    @staticmethod
    def get_packs():
        if not os.path.exists(PACKS_DIR): 
            return []
        packs = [d for d in os.listdir(PACKS_DIR) if os.path.isdir(os.path.join(PACKS_DIR, d))]
        return sorted(packs)

    @staticmethod
    def get_templates():
        if not os.path.exists(TEMPLATES_DIR): 
            return []
        templates = [d for d in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, d))]
        templates = [t for t in templates if not t.endswith("_Dummy")]
        return sorted(templates)

    @staticmethod
    def create_pack(pack_name: str, license_name: str, base_id: int):
        pack_path = os.path.join(PACKS_DIR, pack_name)
        if os.path.exists(pack_path):
            raise ValueError("مجلد الحزمة موجود مسبقاً! يرجى اختيار اسم مختلف.")
            
        os.makedirs(os.path.join(pack_path, "objects_meshes"))
        os.makedirs(os.path.join(pack_path, "objects_textures"))
        os.makedirs(os.path.join(pack_path, "products_icons"))
        
        products_json = {
            "$schema": "../schemas/product_config.json",
            "ProductLicenses": [
                {
                    "ID": base_id,
                    "LicenseName": license_name,
                    "RequiredPlayerLevel": 1,
                    "PurchasingCost": 0,
                    "Products": []
                }
            ]
        }
        
        with open(os.path.join(pack_path, "products.json"), "w", encoding="utf-8") as f:
            json.dump(products_json, f, indent=4, ensure_ascii=False)
            
        return pack_path
