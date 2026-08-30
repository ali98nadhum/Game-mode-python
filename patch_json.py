import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add the shape to the dropdown list
old_dropdown = """        self.shape_dropdown = ctk.CTkOptionMenu(self.tab_add, variable=self.shape_var, values=[
            ar("حجم قياسي (PS4/PS5/Blu-ray)"),
            ar("مربع وسميك (PS1/CD)"),
            ar("نحيف وطويل (Nintendo Switch)"),
            ar("مستطيل عريض (Keyboard)"),
            ar("علبة هاتف (Mobile Phone)")
        ], width=450)"""

new_dropdown = """        self.shape_dropdown = ctk.CTkOptionMenu(self.tab_add, variable=self.shape_var, values=[
            ar("حجم قياسي (PS4/PS5/Blu-ray)"),
            ar("مربع وسميك (PS1/CD)"),
            ar("نحيف وطويل (Nintendo Switch)"),
            ar("مستطيل عريض (Keyboard)"),
            ar("علبة هاتف (Mobile Phone)"),
            ar("كرتون كونسول ضخم (PS4/Xbox)")
        ], width=450)"""
content = content.replace(old_dropdown, new_dropdown)

# 2. Add local_scale logic
old_scale_logic = """            # Determine Box Shape Scale
            if shape_choice == ar("مربع وسميك (PS1/CD)"):
                local_scale = [1.2, 0.7, 2.5]
            elif shape_choice == ar("نحيف وطويل (Nintendo Switch)"):
                local_scale = [1.0, 1.5, 0.8]
            elif shape_choice == ar("مستطيل عريض (Keyboard)"):
                local_scale = [3.3, 1.2, 0.6]
            elif shape_choice == ar("علبة هاتف (Mobile Phone)"):
                local_scale = [0.8, 1.0, 1.2]
            else:
                local_scale = [1.2, 1.2, 1.2]"""

new_scale_logic = """            # Determine Box Shape Scale
            if shape_choice == ar("مربع وسميك (PS1/CD)"):
                local_scale = [1.2, 0.7, 2.5]
            elif shape_choice == ar("نحيف وطويل (Nintendo Switch)"):
                local_scale = [1.0, 1.5, 0.8]
            elif shape_choice == ar("مستطيل عريض (Keyboard)"):
                local_scale = [3.3, 1.2, 0.6]
            elif shape_choice == ar("علبة هاتف (Mobile Phone)"):
                local_scale = [0.8, 1.0, 1.2]
            elif shape_choice == ar("كرتون كونسول ضخم (PS4/Xbox)"):
                local_scale = [2.5, 2.5, 1.5]
            else:
                local_scale = [1.2, 1.2, 1.2]
                
            is_console = (shape_choice == ar("كرتون كونسول ضخم (PS4/Xbox)")) or ("ps" in template_name.lower()) or ("xbox" in template_name.lower()) or ("console" in template_name.lower())
            
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
                product_amount_on_purchase = 20"""
content = content.replace(old_scale_logic, new_scale_logic)

# 3. Inject variables into JSON
old_json = """                "ProductAmountOnPurchase": 20,
                "BasePrice": price,
                "MinDynamicPrice": round(price * 1.5, 2),
                "MaxDynamicPrice": round(price * 2.5, 2),
                "OptimumProfitRate": 100.0,
                "MaxProfitRate": 120.0,
                "GridLayoutInBox": {
                    "boxSize": "_20x10x7",
                    "productCount": 20,
                    "firstObjectPosition": [0.27, -0.01, 0.0],
                    "productAngles": [0.0, 90.0, 0.0],
                    "spacing": [0.028, 0.0, 0.0],
                    "productPlacement": [20,1],
                    "scaleMultiplier": 1.0
                },
                "GridLayoutInStorage": {
                    "boxSize": "_20x10x7",
                    "productCount": 60,
                    "firstObjectPosition": [0.31, 0.01, -0.21],
                    "productAngles": [0.0, 0.0, 0.0],
                    "spacing": [0.21, 0.0, 0.027],
                    "productPlacement": [4,15],
                    "scaleMultiplier": 1.1
                },
                "ItemGridSize": [2, 1]"""
                
new_json = """                "ProductAmountOnPurchase": product_amount_on_purchase,
                "BasePrice": price,
                "MinDynamicPrice": round(price * 1.5, 2),
                "MaxDynamicPrice": round(price * 2.5, 2),
                "OptimumProfitRate": 100.0,
                "MaxProfitRate": 120.0,
                "GridLayoutInBox": grid_in_box,
                "GridLayoutInStorage": grid_in_storage,
                "ItemGridSize": item_grid_size"""
content = content.replace(old_json, new_json)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

