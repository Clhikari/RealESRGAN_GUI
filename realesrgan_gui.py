import os
import subprocess
import customtkinter as ctk
import pywinstyles
from tkinter import filedialog
from threading import Thread
import tkinter as tk
import re
from PIL import Image
import configparser

class RealESRGAN_GUI_Enhanced:
    def __init__(self, master):
        self.master = master
        self.config = configparser.ConfigParser()
        Image.MAX_IMAGE_PIXELS = None
        self.settings_file = './config.ini'
        # --- 外观设置 ---
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        master.title("Real-ESRGAN 超分辨率工具")
        master.geometry("750x750")
        master.resizable(True, True)

        # 应用毛玻璃效果
        try:
            pywinstyles.apply_style(master, style="mica")
        except Exception as e:
            print(f"应用窗口特效失败: {e}")

        self.selected_files = []
        
        # 自定义颜色
        self.primary_color = "#1f6feb"
        self.success_color = "#2ea043"
        self.warning_color = "#d29922"
        self.error_color = "#f85149"
        self.card_bg = "#1c1c1e"
        
        # 动画和进度相关
        self.animation_running = False
        self.current_progress = 0.0
        self.current_image_index = 0
        self.total_images = 0

        # --- 主容器 ---
        main_container = ctk.CTkFrame(master, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- 标题栏 ---
        title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🎨 Real-ESRGAN 图像超分辨率处理",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="批量高质量图像放大工具",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        subtitle_label.pack(side="left", padx=15)

        # --- 标签页容器 ---
        self.tabview = ctk.CTkTabview(main_container, corner_radius=15)
        self.tabview.pack(fill="both", expand=True)
        
        # 创建两个标签页
        self.tabview.add("基础设置")
        self.tabview.add("高级设置")
        
        # 设置标签页样式
        self.tabview._segmented_button.configure(
            fg_color="#2a2a2d",
            selected_color=self.primary_color,
            selected_hover_color="#1557c0"
        )
        
        # 获取标签页容器
        basic_tab = self.tabview.tab("基础设置")
        basic_scroll_frame = ctk.CTkScrollableFrame(basic_tab, fg_color="transparent")
        basic_scroll_frame.pack(fill="both", expand=True)
        advanced_tab = self.tabview.tab("高级设置")
        advanced_scroll_frame = ctk.CTkScrollableFrame(advanced_tab )
        advanced_scroll_frame.pack(fill="both", expand=True)
        # --- 基础设置标签页内容 ---
        config_card = self.create_card(basic_scroll_frame, "⚙️ 基础配置")
        config_card.pack(fill="x", pady=(0, 15))
        
        # 配置内容容器
        config_content = ctk.CTkFrame(config_card, fg_color="transparent")
        config_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # 可执行文件选择
        exe_frame = ctk.CTkFrame(config_content, fg_color="transparent")
        exe_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            exe_frame,
            text="📂 可执行文件",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.exe_path = ctk.StringVar()
        ctk.CTkEntry(
            exe_frame,
            textvariable=self.exe_path,
            corner_radius=8,
            height=35
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            exe_frame,
            text="选择 EXE",
            command=self.browse_exe,
            corner_radius=8,
            width=120,
            fg_color="#404044",
            hover_color="#505054"
        ).pack(side="left")
        
        # 输出文件夹选择
        output_frame = ctk.CTkFrame(config_content, fg_color="transparent")
        output_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            output_frame,
            text="📁 输出文件夹",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.output_folder_path = ctk.StringVar()
        ctk.CTkEntry(
            output_frame,
            textvariable=self.output_folder_path,
            corner_radius=8,
            height=35
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            output_frame,
            text="选择文件夹",
            command=self.browse_output_folder,
            corner_radius=8,
            width=120,
            fg_color="#404044",
            hover_color="#505054"
        ).pack(side="left")
        
        # 参数设置行
        params_frame = ctk.CTkFrame(config_content, fg_color="transparent")
        params_frame.pack(fill="x", pady=(10, 0))
        
        # 第一行：模型和后缀
        params_row1 = ctk.CTkFrame(params_frame, fg_color="transparent")
        params_row1.pack(fill="x", pady=(0, 10))
        
        # 模型选择
        model_container = ctk.CTkFrame(params_row1, fg_color="transparent")
        model_container.pack(side="left", fill="x", expand=True, padx=(0, 7))
        
        model_frame = ctk.CTkFrame(model_container, fg_color="#2a2a2d", corner_radius=10)
        model_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            model_frame, 
            text="🎯 模型",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.model_name = ctk.StringVar(value='realesrgan-x4plus-anime')
        self.model = self.model_name
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            variable=self.model_name,
            values=[
                'realesrgan-x4plus',
                'realesrnet-x4plus',
                'realesrgan-x4plus-anime',
                'realesr-animevideov3'
            ],
            state='readonly',
            corner_radius=8,
            button_color=self.primary_color,
            button_hover_color="#1557c0",
            dropdown_fg_color="#2a2a2d",
            dropdown_hover_color="#3a3a3d",
            dropdown_text_color="white"
        )
        self.model_combo.pack(fill="x", padx=15, pady=(0, 10))
        
        # 输出后缀
        suffix_container = ctk.CTkFrame(params_row1, fg_color="transparent")
        suffix_container.pack(side="left", fill="x", expand=True, padx=(7, 0))
        
        suffix_frame = ctk.CTkFrame(suffix_container, fg_color="#2a2a2d", corner_radius=10)
        suffix_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            suffix_frame,
            text="✏️ 输出后缀",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.suffix = ctk.StringVar(value="_upscaled")
        ctk.CTkEntry(
            suffix_frame,
            textvariable=self.suffix,
            corner_radius=8,
            height=32
        ).pack(fill="x", padx=15, pady=(0, 10))
        self.file_suffix = self.suffix
        # 第二行：放大倍数和输出格式
        params_row2 = ctk.CTkFrame(params_frame, fg_color="transparent")
        params_row2.pack(fill="x", pady=(0, 10))
        
        # 放大倍数
        scale_container = ctk.CTkFrame(params_row2, fg_color="transparent")
        scale_container.pack(side="left", fill="x", expand=True, padx=(0, 7))
        
        scale_frame = ctk.CTkFrame(scale_container, fg_color="#2a2a2d", corner_radius=10)
        scale_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            scale_frame,
            text="🔍 放大倍数",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.scale_ratio = ctk.StringVar(value="4")
        scale_combo = ctk.CTkComboBox(
            scale_frame,
            variable=self.scale_ratio,
            values=["2", "3", "4"],
            state='readonly',
            corner_radius=8,
            button_color=self.primary_color,
            button_hover_color="#1557c0",
            dropdown_fg_color="#2a2a2d",
            dropdown_hover_color="#3a3a3d",
            dropdown_text_color="white",
            width=120
        )
        scale_combo.pack(fill="x", padx=15, pady=(0, 10))
        
        # 输出格式
        format_container = ctk.CTkFrame(params_row2, fg_color="transparent")
        format_container.pack(side="left", fill="x", expand=True, padx=(7, 0))
        
        format_frame = ctk.CTkFrame(format_container, fg_color="#2a2a2d", corner_radius=10)
        format_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            format_frame,
            text="🖼️ 输出格式",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.output_format = ctk.StringVar(value="保持原格式")
        format_combo = ctk.CTkComboBox(
            format_frame,
            variable=self.output_format,
            values=[
                "保持原格式",
                "PNG",
                "JPEG",
                "WebP",
                "BMP",
                "TIFF"
            ],
            state='readonly',
            corner_radius=8,
            button_color=self.primary_color,
            button_hover_color="#1557c0",
            dropdown_fg_color="#2a2a2d",
            dropdown_hover_color="#3a3a3d",
            dropdown_text_color="white"
        )
        format_combo.pack(fill="x", padx=15, pady=(0, 10))
        
        # 格式转换设置行（仅在选择JPEG或WebP时显示质量设置）
        quality_container = ctk.CTkFrame(params_frame, fg_color="transparent")
        quality_container.pack(side="left", fill="x", expand=True, padx=(14, 0))
        
        quality_frame = ctk.CTkFrame(quality_container, fg_color="#2a2a2d", corner_radius=10)
        quality_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            quality_frame,
            text="⚡ 压缩质量",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        quality_inner = ctk.CTkFrame(quality_frame, fg_color="transparent")
        quality_inner.pack(fill="x", padx=15, pady=(0, 10))
        
        self.quality_value = ctk.IntVar(value=95)
        self.quality_label = ctk.CTkLabel(
            quality_inner,
            text="95",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.primary_color,
            width=30
        )
        self.quality_label.pack(side="right", padx=(5, 0))
        
        self.quality_slider = ctk.CTkSlider(
            quality_inner,
            from_=60,
            to=100,
            number_of_steps=40,
            variable=self.quality_value,
            command=self.update_quality_label,
            button_color=self.primary_color,
            button_hover_color="#1557c0",
            progress_color=self.primary_color
        )
        self.quality_slider.pack(side="left", fill="x", expand=True)

        # --- 文件选择卡片 ---
        files_card = self.create_card(basic_scroll_frame, "🖼️ 图片文件")
        files_card.pack(fill="x", pady=(0, 15))
        
        files_inner = ctk.CTkFrame(files_card, fg_color="transparent")
        files_inner.pack(fill="x", padx=15, pady=(0, 15))
        
        self.files_selected_status = ctk.StringVar(value="未选择任何文件")
        status_frame = ctk.CTkFrame(files_inner, fg_color="#2a2a2d", corner_radius=8, height=50)
        status_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        status_frame.pack_propagate(False)
        
        self.status_icon = ctk.CTkLabel(
            status_frame,
            text="⚪",
            font=ctk.CTkFont(size=20)
        )
        self.status_icon.pack(side="left", padx=15)
        
        self.files_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.files_selected_status,
            font=ctk.CTkFont(size=13)
        )
        self.files_label.pack(side="left", fill="x", expand=True)
        
        self.select_files_btn = ctk.CTkButton(
            files_inner,
            text="选择图片",
            command=self.browse_files,
            corner_radius=8,
            height=50,
            width=120,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.primary_color,
            hover_color="#1557c0"
        )
        self.select_files_btn.pack(side="left")

        # --- 处理控制卡片 ---
        control_card = self.create_card(basic_scroll_frame, "🚀 处理控制")
        control_card.pack(fill="x", pady=(0, 15))
        
        control_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        control_inner.pack(fill="x", padx=15, pady=(0, 15))
        
        self.start_button = ctk.CTkButton(
            control_inner,
            text="▶ 开始处理",
            command=self.start_processing_thread,
            corner_radius=10,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.success_color,
            hover_color="#2b8a3e"
        )
        self.start_button.pack(fill="x", pady=(0, 15))
        
        # 进度条
        progress_frame = ctk.CTkFrame(control_inner, fg_color="transparent")
        progress_frame.pack(fill="x")
        
        self.progress = ctk.CTkProgressBar(
            progress_frame,
            corner_radius=8,
            height=20,
            progress_color=self.primary_color
        )
        self.progress.pack(fill="x", pady=(0, 8))
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="💡 欢迎使用！请选择文件和配置参数",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.status_label.pack(anchor="w")

        # --- 日志卡片 ---
        log_card = self.create_card(basic_scroll_frame, "📋 处理日志")
        log_card.pack(fill="both", expand=True)
        
        self.log_area = ctk.CTkTextbox(
            log_card,
            wrap=tk.WORD,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#1a1a1c"
        )
        self.log_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_area.configure(state='disabled')
        
        # --- 高级设置标签页内容 ---
        
        # GPU 设置卡片
        gpu_card = self.create_card(advanced_scroll_frame, "🎮 GPU 设置")
        gpu_card.pack(fill="x", pady=(0, 15))
        
        gpu_content = ctk.CTkFrame(gpu_card, fg_color="transparent")
        gpu_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # GPU ID
        gpu_id_frame = ctk.CTkFrame(gpu_content, fg_color="transparent")
        gpu_id_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            gpu_id_frame,
            text="🎮 GPU ID",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.gpu_id = ctk.StringVar(value="auto")
        ctk.CTkEntry(
            gpu_id_frame,
            textvariable=self.gpu_id,
            corner_radius=8,
            height=35,
            placeholder_text="auto/0/1/2 或多GPU: 0,1,2"
        ).pack(side="left", fill="x", expand=True)
        self.GPU_ID =self.gpu_id
        # Tile Size
        tile_frame = ctk.CTkFrame(gpu_content, fg_color="transparent")
        tile_frame.pack(fill="x")
        
        ctk.CTkLabel(
            tile_frame,
            text="📐 Tile Size",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.tile_size = ctk.StringVar(value="0")
        tile_entry = ctk.CTkEntry(
            tile_frame,
            textvariable=self.tile_size,
            corner_radius=8,
            height=35,
            placeholder_text="0=自动，或设置固定值（≥32）"
        )
        tile_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            tile_frame,
            text="💡 显存不足时降低此值",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        ).pack(side="left")
        
        # 性能优化卡片
        performance_card = self.create_card(advanced_scroll_frame, "⚡ 性能优化")
        performance_card.pack(fill="x", pady=(0, 15))
        
        performance_content = ctk.CTkFrame(performance_card, fg_color="transparent")
        performance_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # 线程设置
        thread_frame = ctk.CTkFrame(performance_content, fg_color="transparent")
        thread_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            thread_frame,
            text="⚙️ 线程数",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w"
        ).pack(side="left", padx=(0, 10))
        
        self.thread_count = ctk.StringVar(value="1:2:2")
        ctk.CTkEntry(
            thread_frame,
            textvariable=self.thread_count,
            corner_radius=8,
            height=35,
            placeholder_text="格式: load:proc:save"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.thread_num = self.thread_count
        ctk.CTkLabel(
            thread_frame,
            text="💡 默认 1:2:2",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        ).pack(side="left")
        
        # TTA 模式
        tta_frame = ctk.CTkFrame(performance_content, fg_color="#2a2a2d", corner_radius=10)
        tta_frame.pack(fill="x")
        
        tta_inner = ctk.CTkFrame(tta_frame, fg_color="transparent")
        tta_inner.pack(fill="x", padx=15, pady=15)
        
        self.enable_tta = ctk.BooleanVar(value=False)
        tta_switch = ctk.CTkSwitch(
            tta_inner,
            text="✨ 启用 TTA 模式（更高质量，处理更慢）",
            variable=self.enable_tta,
            onvalue=True,
            offvalue=False,
            progress_color=self.primary_color,
            button_color=self.primary_color,
            button_hover_color="#1557c0",
            font=ctk.CTkFont(size=13)
        )
        tta_switch.pack(anchor="w")
        self.TAA = self.enable_tta
        # 说明卡片
        info_card = self.create_card(advanced_scroll_frame, "📖 参数说明")
        info_card.pack(fill="both", expand=True)
        
        info_text = ctk.CTkTextbox(
            info_card,
            wrap=tk.WORD,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#1a1a1c",
            height=200
        )
        info_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        info_content = """📚 参数详细说明：

                🎮 GPU ID:
                • auto - 自动选择最佳GPU
                • 0/1/2 - 指定单个GPU
                • 0,1,2 - 使用多个GPU并行处理

                📐 Tile Size:
                • 0 - 自动计算（推荐）
                • 固定值 - 手动设置（如256、512）
                • 显存不足时降低此值可避免崩溃
                • 多GPU可用: 0,0,0

                ⚙️ 线程数:
                • 格式: load:proc:save
                • load - 加载图片的线程数
                • proc - 处理图片的线程数  
                • save - 保存图片的线程数
                • 多GPU: 1:2,2,2:2

                ✨ TTA 模式:
                • Test-Time Augmentation
                • 通过多次推理提升质量
                • 处理时间增加约8倍
                • 适合对质量要求极高的场景"""
        
        info_text.insert("1.0", info_content)
        info_text.configure(state='disabled')
        self.load_settings()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)


    def create_card(self, parent, title):
        """创建卡片容器"""
        card = ctk.CTkFrame(parent, fg_color=self.card_bg, corner_radius=15)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(15, 10))
        
        return card

    def browse_exe(self):
        file = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if file:
            self.file_exe = file
            self.exe_path.set(file)
            self.log(f"✅ 已选择可执行文件: {os.path.basename(file)}")

    def browse_files(self):
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if files:
            self.selected_files = files
            self.files_selected_status.set(f"已选择 {len(files)} 个文件")
            self.animate_icon_change()
            self.log(f"✅ 已选择 { len(files)} 个图片文件")

    def update_quality_label(self, value):
        """更新质量滑块标签"""
        self.quality_label.configure(text=str(int(float(value))))
        self.compression = self.quality_label

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output = folder
            self.output_folder_path.set(folder)
            self.log(f"✅ 已选择输出文件夹: {folder}")

    def log(self, message):
        # 确保UI操作在主线程中执行
        def _update_log():
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
        self.master.after(0, _update_log)

    def update_progress_from_percentage(self, percentage, filename):
        """根据当前图片的百分比更新总进度"""
        # 计算当前图片在总进度中的权重
        single_image_weight = 1.0 / self.total_images
        # 当前图片之前已完成的进度
        previous_progress = (self.current_image_index - 1) / self.total_images
        # 当前图片的进度贡献
        current_image_progress = (percentage / 100.0) * single_image_weight
        # 总进度
        total_progress = previous_progress + current_image_progress
        
        # 更新进度条和状态
        def _update():
            self.progress.set(total_progress)
            self.status_label.configure(
                text=f"🔄 正在处理: {filename} - {percentage:.1f}% ({self.current_image_index}/{self.total_images})",
                text_color="white"
            )
        self.master.after(0, _update)

    def start_processing_thread(self):
        self.start_button.configure(state="disabled", text="⏳ 处理中...")
        self.animate_button_click()
        
        # 清空日志区域
        self.log_area.configure(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.configure(state='disabled')
        
        # 重置进度
        self.current_progress = 0.0
        self.progress.set(0)

        self.processing_thread = Thread(target=self.process_images, daemon=True)
        self.processing_thread.start()

    def process_images(self):
        exe_path = self.exe_path.get()
        output_dir = self.output_folder_path.get()
        model = self.model_name.get()
        suffix = self.suffix.get()
        output_format = self.output_format.get()
        scale = self.scale_ratio.get()
        tile_size = self.tile_size.get()
        gpu_id = self.gpu_id.get()
        thread_count = self.thread_count.get()
        enable_tta = self.enable_tta.get()
        
        if not all([os.path.isfile(exe_path), self.selected_files, os.path.isdir(output_dir)]):
            def _update_error():
                self.status_label.configure(
                    text="❌ 错误: 请检查所有路径和文件选择是否正确",
                    text_color=self.error_color
                )
                self.start_button.configure(state="normal", text="▶ 开始处理")
            self.master.after(0, _update_error)
            return
        
        self.total_images = len(self.selected_files)
        success_count = 0
        
        for i, input_file_path in enumerate(self.selected_files):
            self.current_image_index = i + 1
            filename = os.path.basename(input_file_path)

            base, ext = os.path.splitext(filename)
            temp_output_path = os.path.join(output_dir, f"{base}{suffix}{ext}")

            # 最终输出文件（可能转换格式）
            if output_format == "保持原格式":
                final_output_path = temp_output_path
                final_ext = ext
            else:
                format_map = {
                    "PNG": ".png",
                    "JPEG": ".jpg",
                    "WebP": ".webp",
                    "BMP": ".bmp",
                    "TIFF": ".tiff"
                }
                final_ext = format_map.get(output_format, ext)
                final_output_path = os.path.join(output_dir, f"{base}{suffix}{final_ext}")
                
            output_filename = os.path.basename(final_output_path)

            # 读取原图尺寸
            with Image.open(input_file_path) as img:
                src_width, src_height = img.size

            # 计算目标尺寸（根据用户选择的倍数）
            scale_value = int(scale)
            target_width = src_width * scale_value
            target_height = src_height * scale_value

            # 模型默认放大倍数
            model_factor = 4
            upscaled_width = src_width * model_factor
            upscaled_height = src_height * model_factor
            # 构建命令行参数
            command = [
                exe_path,
                '-i', input_file_path,
                '-o', final_output_path,
                '-n', model,
            ]
            
            # 添加可选参数
            if tile_size and tile_size != "0":
                command.extend(['-t', tile_size])
            
            if gpu_id and gpu_id.lower() != "auto":
                command.extend(['-g', gpu_id])
            
            if thread_count and thread_count != "1:2:2":
                command.extend(['-j', thread_count])
            
            if enable_tta:
                command.append('-x')
            
            # 添加详细输出
            command.append('-v')
            
            self.log(f"\n{'='*60}\n▶ 开始处理: {filename}\n💻 命令: {' '.join(command)}\n{'='*60}")
            
            try:
                # 使用 Popen 启动子进程，并重定向输出流
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                # 实时读取并记录输出，同时解析百分比
                for line in iter(process.stdout.readline, ''): # type: ignore
                    if line:
                        stripped_line = line.strip()
                        self.log(stripped_line)
                        
                        # 尝试从输出中提取百分比（匹配如 "98.61%" 的模式）
                        percentage_match = re.search(r'(\d+\.?\d*)%', stripped_line)
                        if percentage_match:
                            try:
                                percentage = float(percentage_match.group(1))
                                self.update_progress_from_percentage(percentage, filename)
                            except ValueError:
                                pass
                
                # 等待进程结束并获取返回码
                process.stdout.close() # type: ignore
                return_code = process.wait()

                # 根据返回码判断成功或失败
                if return_code == 0:
                    # 如果目标尺寸不等于模型输出尺寸，需要降采样
                    if scale_value != model_factor:
                        self.log(f"🔄 降采样: {upscaled_width}x{upscaled_height} → {target_width}x{target_height}")
                        
                        try:
                            with Image.open(final_output_path) as img:
                                # 使用高质量的 Lanczos 算法降采样
                                resized = img.resize(
                                    (target_width, target_height), 
                                    Image.Resampling.LANCZOS
                                )
                                resized.save(final_output_path)
                                
                        except Exception as e:
                            self.log(f"❌ 降采样失败: {e}")
                            continue
                    else:
                        # 尺寸相同，直接重命名
                        if temp_output_path != final_output_path:
                            os.rename(temp_output_path, final_output_path)
                    
                    self.log(f"✅ 成功: {filename} 已保存为 {output_filename}")
                    success_count += 1


            except FileNotFoundError:
                self.log(f"❌ 致命错误: 未找到可执行文件 '{exe_path}'。请检查路径。")
                break
            except Exception as e:
                self.log(f"❌ 发生意外错误: {e}")
                break

        # 处理完成
        def _update_completion():
            self.status_label.configure(
                text=f"✨ 处理完成！成功: {success_count}/{self.total_images}",
                text_color=self.success_color
            )
            self.start_button.configure(state="normal", text="▶ 开始处理")
            self.progress.set(1.0)
        self.master.after(0, _update_completion)
        
        self.animate_completion()
        self.log(f"\n{'='*60}\n🎉 批量处理完成！\n✅ 成功: {success_count}/{self.total_images}\n{'='*60}")
    
    # === 动画效果函数 ===
    
    def animate_icon_change(self):
        """图标切换动画 - 淡入淡出效果"""
        icons = ["⚪", "🔵", "✅"]
        colors = ["white", "#1f6feb", "#2ea043"]
        
        def transition(step=0):
            if step < len(icons):
                self.status_icon.configure(text=icons[step])
                self.files_label.configure(text_color=colors[step])
                self.master.after(80, lambda: transition(step + 1))
        
        transition()
    
    def animate_button_click(self):
        """按钮点击动画 - 缩放效果"""
        original_height = 45
        
        def scale_down():
            self.start_button.configure(height=40)
            self.master.after(50, scale_up)
        
        def scale_up():
            self.start_button.configure(height=original_height)
        
        scale_down()
    
    def animate_completion(self):
        """完成动画 - 进度条闪烁效果"""
        colors = [self.primary_color, self.success_color, self.primary_color, self.success_color]
        
        def flash(step=0):
            if step < len(colors):
                self.progress.configure(progress_color=colors[step])
                self.master.after(150, lambda: flash(step + 1))
            else:
                self.progress.configure(progress_color=self.success_color)
        
        flash()
    
    def on_closing(self):
        """处理窗口关闭事件。"""
        self.save_settings()
        self.master.destroy()

    def save_settings(self):
        try:
            self.config['DEFAULT'] = {
                'exe_path': self.exe_path.get(),
                'output_folder': self.output_folder_path.get(),
                'model': self.model_name.get(),
                'suffix': self.suffix.get(),
                'scale': self.scale_ratio.get(),
                'format': self.output_format.get(),
                'compression': str(self.quality_value.get()),
                'gpu_id': self.gpu_id.get(),
                'tile_size': self.tile_size.get(),
                'threads': self.thread_count.get(),
                'tta': str(self.enable_tta.get())
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
                self.log("⚙️ 设置已保存。")
        except Exception as e:
                self.log(f"❌ 保存设置失败: {e}")

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            self.log("💡 未找到配置文件，将使用默认设置。")
            return
        try:
            self.config.read(self.settings_file, encoding='utf-8')
            settings = self.config['DEFAULT']
            self.exe_path.set(settings.get('exe_path', ''))
            self.output_folder_path.set(settings.get('output_folder', ''))
            self.model_name.set(settings.get('model', ''))
            self.suffix.set(settings.get('suffix', ''))
            self.scale_ratio.set(settings.get('scale', ''))
            self.output_format.set(settings.get('format', ''))
            self.quality_value.set(int(settings.getint('compression', '')))
            self.gpu_id.set(settings.get('gpu_id', ''))
            self.tile_size.set(settings.get('tile_size', ''))
            self.thread_count.set(settings.get('threads',''))
            self.enable_tta.set(bool(settings.getboolean('taa', '')))
            self.update_quality_label(self.quality_value.get())
            self.log("⚙️ 设置已加载。")
        except Exception as e:
            self.log(f"❌ 加载设置失败: {e}")


if __name__ == '__main__':
    app = ctk.CTk()
    try:
        app.iconbitmap("./icon/icon.ico") 
    except Exception as e:
        print(f"设置图标失败: {e}")
    gui = RealESRGAN_GUI_Enhanced(app)
    app.mainloop()