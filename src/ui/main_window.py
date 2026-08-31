import customtkinter as ctk
from src.utils.helpers import ar
from src.ui.views.create_pack_view import CreatePackView
from src.ui.views.custom_item_view import CustomItemView

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(ar("صانع مودات سوبر ماركت سيميوليتر - النسخة الاحترافية"))
        self.geometry("900x700")
        self.minsize(800, 600)

        # Configure grid layout (1 row, 2 columns: sidebar and main content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ModMaker\nCore", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Sidebar Buttons
        self.btn_create_pack = ctk.CTkButton(self.sidebar_frame, text=ar("إنشاء حزمة جديدة"), command=self.show_create_pack_view, height=40, font=("Arial", 15, "bold"))
        self.btn_create_pack.grid(row=1, column=0, padx=20, pady=10)

        self.btn_custom_item = ctk.CTkButton(self.sidebar_frame, text=ar("إضافة منتج مخصص"), command=self.show_custom_item_view, height=40, font=("Arial", 15, "bold"))
        self.btn_custom_item.grid(row=2, column=0, padx=20, pady=10)
        
        # 2. Main Content Frame
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Initialize Views
        self.create_pack_view = CreatePackView(self.main_content_frame, refresh_callback=self.refresh_views)
        self.custom_item_view = CustomItemView(self.main_content_frame)

        # Show default view
        self.show_create_pack_view()

    def refresh_views(self):
        """Called when a new pack is created so the other views can update their dropdowns"""
        self.custom_item_view.refresh_data()

    def show_create_pack_view(self):
        self.custom_item_view.grid_forget()
        self.create_pack_view.grid(row=0, column=0, sticky="nsew")
        
        # Highlight button
        self.btn_create_pack.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.btn_custom_item.configure(fg_color="transparent", border_width=2)

    def show_custom_item_view(self):
        self.create_pack_view.grid_forget()
        self.custom_item_view.grid(row=0, column=0, sticky="nsew")
        self.custom_item_view.refresh_data()
        
        # Highlight button
        self.btn_custom_item.configure(fg_color=["#3B8ED0", "#1F6AA5"], border_width=0)
        self.btn_create_pack.configure(fg_color="transparent", border_width=2)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
