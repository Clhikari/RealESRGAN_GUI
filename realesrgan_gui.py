import os
import subprocess
import customtkinter as ctk
import pywinstyles
from tkinter import filedialog
from threading import Thread
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
import re
from PIL import Image
import configparser
import sys


# 创建支持拖拽的窗口类
class TkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class RealESRGAN_GUI_Enhanced:
    def __init__(self, master):
        self.master = master
        self.config = configparser.ConfigParser()
        Image.MAX_IMAGE_PIXELS = None
        
        base_path = self.get_app_path()
        self.settings_file = os.path.join(base_path, 'config.ini')
        self.stop_event = False
        self.current_process = None
        # --- 外观设置 ---
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        master.title("Real-ESRGAN工具")
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
        
        self.scale_ratio = ctk.StringVar(value="4.0")
        scale_combo = ctk.CTkEntry(
            scale_frame,
            textvariable=self.scale_ratio,
            corner_radius=8,
            width=120,
            height=32,
            placeholder_text="例如: 2.0, 2.5, 4.0"
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
            from_=10,
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
        # 注册显示文件名的深色框
        self._register_drag_drop(status_frame)
        # 注册外层容器
        self._register_drag_drop(files_inner)
        
        self.status_icon = ctk.CTkLabel(
            status_frame,
            text="⚪",
            font=ctk.CTkFont(size=20)
        )
        self.status_icon.pack(side="left", padx=15)
        
        # 注册status_icon容器
        self._register_drag_drop(self.status_icon)
        
        self.files_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.files_selected_status,
            font=ctk.CTkFont(size=13)
        )
        self.files_label.pack(side="left", fill="x", expand=True)
        
        # 注册lable容器
        self._register_drag_drop(self.files_label)
        
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
        self.select_files_btn.pack(side="left", padx=(0, 10))
        
        self.manage_btn = ctk.CTkButton(
            files_inner,
            text="📋",
            command=self.open_file_manager,
            corner_radius=8,
            height=50,
            width=50,
            font=ctk.CTkFont(size=20),
            fg_color="#3a3a3d",
            hover_color="#4a4a4d"
        )
        
        self.manage_btn.pack(side="left")
        self.select_files_btn.pack(side="left")

        # --- 处理控制卡片 ---
        control_card = self.create_card(basic_scroll_frame, "🚀 处理控制")
        control_card.pack(fill="x", pady=(0, 15))
        
        control_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        control_inner.pack(fill="x", padx=15, pady=(0, 15))
        self.stop_button = ctk.CTkButton(
        control_inner,  # 替换为你实际的父容器变量名
        text="⏹ 停止处理", 
        fg_color="#D32F2F",  # 红色警示色
        hover_color="#B71C1C",
        state="disabled",    # 初始状态不可点
        command=self.stop_processing
        )
        self.stop_button.pack(fill="x", pady=(10, 0)) # 根据你的布局调整
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
                • 推理时间大量增加，质量提升微乎其微不建议开启"""
        
        info_text.insert("1.0", info_content)
        info_text.configure(state='disabled')
        self.load_settings()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    
    def _register_drag_drop(self, widget):
        """辅助函数：为 CTk 组件及其内部控件注册拖拽事件"""
        try:
            # 尝试直接注册（针对原生 tkinter 组件）
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self.drop_files)
        except AttributeError:
            # 如果是 CTk 组件，尝试注册其内部的核心控件
            if hasattr(widget, '_canvas'):
                widget._canvas.drop_target_register(DND_FILES)
                widget._canvas.dnd_bind('<<Drop>>', self.drop_files)
            
            # 注册内部 Label (CTkLabel, CTkButton 的文字部分)
            if hasattr(widget, '_text_label'): # CTkButton 的文字
                widget._text_label.drop_target_register(DND_FILES)
                widget._text_label.dnd_bind('<<Drop>>', self.drop_files)
            if hasattr(widget, '_label'): # CTkLabel 的核心
                widget._label.drop_target_register(DND_FILES)
                widget._label.dnd_bind('<<Drop>>', self.drop_files)
            
            # 递归注册所有子组件（防止拖到图标或文字上没反应）
            for child in widget.winfo_children():
                self._register_drag_drop(child)
    
    def get_app_path(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        return application_path

    def stop_processing(self):
        """响应停止按钮点击"""
        if not self.is_processing:
            return

        self.log("🛑 正在尝试停止任务...")
        self.stop_event = True
        
        if self.current_process:
            try:
                self.current_process.kill() # 强制终止进程
                self.log("🛑 已强制终止当前子进程。")
            except Exception as e:
                self.log(f"⚠️ 终止进程时出错: {e}")

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
            current_files = list(self.selected_files) if isinstance(self.selected_files, (list, tuple)) else []
            new_files = list(files)
            for f in new_files:
                if f not in current_files:
                    current_files.append(f)
            self.selected_files = current_files
            self.update_file_status()
            
    def parse_dropped_files(self, data):
        """解析拖拽进来的文件路径字符串（处理 Windows 路径的大括号问题）"""
        filepaths = []
        # 正则表达式匹配：要么是被 {} 包裹的内容，要么是无空格的字符串
        import re
        # 匹配 {C:/path with space/file.jpg} 或 C:/path/file.jpg
        pattern = r'\{.*?\}|\S+'
        matches = re.findall(pattern, data)
        
        for match in matches:
            # 去除可能存在的大括号
            path = match.strip('{}')
            if os.path.isfile(path):
                # 检查是否是图片格式
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')):
                    filepaths.append(path)
        
        return tuple(filepaths)

    def drop_files(self, event):
        """处理拖拽释放事件"""
        files = self.parse_dropped_files(event.data)
        
        if files:
            current_files = list(self.selected_files) if isinstance(self.selected_files, (list, tuple)) else []
            new_files = list(files)
            
            for f in new_files:
                if f not in current_files:
                    current_files.append(f)
            self.selected_files = current_files
            self.update_file_status()
        else:
            self.log("⚠️ 拖拽的文件无效或不是支持的图片格式")
    
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
        
        # 获取压缩质量数值
        quality_val = self.quality_value.get()

        self.stop_event = False
        self.is_processing = True
        
        if not all([os.path.isfile(exe_path), self.selected_files, os.path.isdir(output_dir)]):
            def _update_error():
                self.status_label.configure(
                    text="❌ 错误: 请检查所有路径和文件选择是否正确",
                    text_color=self.error_color
                )
                self.start_button.configure(state="normal", text="▶ 开始处理")
            self.master.after(0, _update_error)
            return

        self.master.after(0, lambda: self.start_button.configure(state="disabled", text="⏳ 处理中..."))
        self.master.after(0, lambda: self.stop_button.configure(state="normal"))
        
        self.total_images = len(self.selected_files)
        success_count = 0
        
        for i, input_file_path in enumerate(self.selected_files):
            if self.stop_event:
                self.log("⚠️ 用户已取消后续任务。")
                break
            self.current_image_index = i + 1
            filename = os.path.basename(input_file_path)
            base, ext = os.path.splitext(filename)

            # 定义一个临时的无损 PNG 路径供 EXE 输出使用
            temp_png_filename = f"temp_{base}_{suffix}.png"
            temp_output_path = os.path.join(output_dir, temp_png_filename)

            # 定义最终输出路径
            format_map = {
                "保持原格式": ext,
                "PNG": ".png",
                "JPEG": ".jpg",
                "WebP": ".webp",
                "BMP": ".bmp",
                "TIFF": ".tiff"
            }
            final_ext = format_map.get(output_format, ext)
            # 如果保持原格式且原格式不是 jpg/webp 等，PIL save 时需要处理
            if output_format == "保持原格式":
                # 简单处理：如果原图是 jpg，最终也是 jpg
                pass 
            
            final_output_path = os.path.join(output_dir, f"{base}{suffix}{final_ext}")
            output_filename = os.path.basename(final_output_path)

            # --- 计算尺寸 ---
            try:
                with Image.open(input_file_path) as img:
                    src_width, src_height = img.size
            except Exception as e:
                self.log(f"❌ 无法读取原图尺寸: {e}")
                continue

            scale_value = float(scale)
            target_width = int(src_width * scale_value)
            target_height = int(src_height * scale_value)

            # --- 构建命令 ---
            # 强制输出为 temp_output_path (PNG)
            command = [
                exe_path,
                '-i', input_file_path,
                '-o', temp_output_path,
                '-n', model,
                '-f', 'png' # 强制 EXE 输出 PNG 格式以保真
            ]
            
            if tile_size and tile_size != "0":
                command.extend(['-t', tile_size])
            if gpu_id and gpu_id.lower() != "auto":
                command.extend(['-g', gpu_id])
            if thread_count and thread_count != "1:2:2":
                command.extend(['-j', thread_count])
            if enable_tta:
                command.append('-x')
            command.append('-v')
            
            self.log(f"\n{'='*60}\n▶ 开始处理: {filename}\n{'='*60}")
            
            try:
                # --- 执行子进程 ---
                self.current_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                for line in iter(self.current_process.stdout.readline, ''):
                    if self.stop_event:
                        self.current_process.kill()
                        break 
                    if line:
                        stripped_line = line.strip()
                        self.log(stripped_line)
                        percentage_match = re.search(r'(\d+\.?\d*)%', stripped_line)
                        if percentage_match:
                            try:
                                percentage = float(percentage_match.group(1))
                                self.update_progress_from_percentage(percentage, filename)
                            except ValueError:
                                pass
                
                self.current_process.stdout.close()
                return_code = self.current_process.wait()
                self.current_process = None

                if self.stop_event:
                    break

                if return_code == 0 and os.path.exists(temp_output_path):
                    # --- 后处理 (Resize, 格式转换, 压缩) ---
                    self.log(f"⚙️ 正在进行后期处理与压缩 (质量: {quality_val})...")
                    
                    try:
                        with Image.open(temp_output_path) as img:
                            # 1. 处理 Resize (如果需要)
                            if img.width != target_width or img.height != target_height:
                                self.log(f"🔄 调整尺寸: {img.width}x{img.height} → {target_width}x{target_height}")
                                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                            
                            # 2. 准备保存参数
                            save_kwargs = {}
                            
                            # 确定保存格式字符串 (PIL 需要 'JPEG' 而不是 '.jpg')
                            pil_format = None
                            ext_lower = final_ext.lower()
                            
                            if '.jpg' in ext_lower or '.jpeg' in ext_lower:
                                pil_format = 'JPEG'
                                save_kwargs['quality'] = quality_val # 应用质量参数
                                if img.mode == 'RGBA':
                                    img = img.convert('RGB') # JPEG 不支持透明通道
                                    
                            elif '.webp' in ext_lower:
                                pil_format = 'WEBP'
                                save_kwargs['quality'] = quality_val # 应用质量参数
                                
                            elif '.png' in ext_lower:
                                pil_format = 'PNG'
                                
                            elif '.bmp' in ext_lower:
                                pil_format = 'BMP'
                            elif '.tiff' in ext_lower:
                                pil_format = 'TIFF'

                            # 3. 保存最终文件
                            img.save(final_output_path, format=pil_format, **save_kwargs)
                            
                        success_count += 1
                        self.log(f"✅ 成功: 已保存为 {output_filename}")

                    except Exception as e:
                        self.log(f"❌ 后期处理失败: {e}")
                    finally:
                        # 清理临时文件
                        if os.path.exists(temp_output_path):
                            try:
                                os.remove(temp_output_path)
                            except:
                                pass
                else:
                    self.log(f"❌ 处理失败或未生成临时文件")

            except FileNotFoundError:
                self.log(f"❌ 致命错误: 未找到可执行文件 '{exe_path}'")
                break
            except Exception as e:
                self.log(f"❌ 发生意外错误: {e}")
                break
            finally:
                self.is_processing = False
                self.current_process = None
                
                def _reset_ui():
                    self.start_button.configure(state="normal", text="▶ 开始处理")
                    self.stop_button.configure(state="disabled")
                    if self.stop_event:
                        self.status_label.configure(text="⛔ 任务已停止", text_color="orange")
                    else:
                        self.status_label.configure(text=f"✨ 全部完成! 成功: {success_count}/{self.total_images}", text_color="green")
                self.master.after(0, _reset_ui)

        def _update_completion():
            self.status_label.configure(text=f"✨ 处理完成！成功: {success_count}/{self.total_images}", text_color=self.success_color)
            self.start_button.configure(state="normal", text="▶ 开始处理")
            self.progress.set(1.0)
        self.master.after(0, _update_completion)
        
        self.animate_completion()
        self.log(f"\n{'='*60}\n🎉 批量处理完成！\n✅ 成功: {success_count}/{self.total_images}\n{'='*60}")
    
    # === 动画效果函数 ===
    def update_file_status(self):
        """辅助函数：更新主界面的文件数量提示"""
        count = len(self.selected_files)
        if count == 0:
            self.files_selected_status.set("未选择任何文件 (支持拖拽)")
            self.status_icon.configure(text="⚪")
        else:
            self.files_selected_status.set(f"已选择 {count} 个文件")
            self.status_icon.configure(text="✅")
            self.log(f"📂 当前文件列表共 {count} 个文件")

    def open_file_manager(self):
        """打开文件管理弹窗"""
        if not self.selected_files:
            self.log("⚠️ 列表为空，无需管理")
            return

        # 创建弹窗
        top = ctk.CTkToplevel(self.master)
        top.title("文件列表管理")
        top.geometry("500x400")
        top.transient(self.master) # 设置为工具窗口
        top.grab_set() # 模态窗口（禁止操作主窗口直到关闭此窗口）
        
        # 标题栏
        header = ctk.CTkFrame(top, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header, text=f"已选文件 ({len(self.selected_files)})", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        ctk.CTkButton(
            header, text="清空全部", width=80, height=30, 
            fg_color=self.error_color, hover_color="#c62828",
            command=lambda: [self.selected_files.clear(), self.update_file_status(), top.destroy()]
        ).pack(side="right")

        # 滚动列表区域
        scroll_frame = ctk.CTkScrollableFrame(top)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 渲染列表
        self.render_file_list(scroll_frame, top)

    def truncate_filename(self, filename, max_length=35):
        """
        辅助函数：如果文件名太长，保留头尾，中间用 ... 代替
        例如: 20251019_very_long_name_upscaled.jpg -> 20251019...upscaled.jpg
        """
        if len(filename) <= max_length:
            return filename
        
        # 保留前15个字符，保留后15个字符（包含后缀）
        head = 15
        tail = 15
        return filename[:head] + "..." + filename[-tail:]

    def render_file_list(self, parent_frame, top_window):
        """渲染文件列表项（修复布局问题）"""
        # 清空现有显示
        for widget in parent_frame.winfo_children():
            widget.destroy()

        for i, file_path in enumerate(self.selected_files):
            # 创建每一行的容器
            row = ctk.CTkFrame(parent_frame, fg_color="#2b2b2b")
            row.pack(fill="x", pady=2)
            
            del_btn = ctk.CTkButton(
                row, 
                text="❌", 
                width=30, 
                height=30,
                fg_color="transparent", 
                hover_color="#404040", 
                text_color="#ff5555",
                command=lambda f=file_path: self.remove_file(f, parent_frame, top_window)
            )
            del_btn.pack(side="right", padx=5)

            # 处理长文件名
            filename = os.path.basename(file_path)
            display_name = self.truncate_filename(filename)

            label = ctk.CTkLabel(
                row, 
                text=f"{i+1}. {display_name}", 
                anchor="w"
            )
            label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

    def remove_file(self, file_path, parent_frame, top_window):
        """从列表中移除指定文件"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self.update_file_status()
            
            # 如果删完了，直接关闭窗口
            if not self.selected_files:
                top_window.destroy()
            else:
                # 重新渲染列表
                self.render_file_list(parent_frame, top_window)
                # 更新窗口标题数量
                for widget in top_window.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, ctk.CTkLabel):
                                child.configure(text=f"已选文件 ({len(self.selected_files)})")
    
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
            self.enable_tta.set(bool(settings.getboolean('tta', '')))
            self.update_quality_label(self.quality_value.get())
            self.log("⚙️ 设置已加载。")
        except Exception as e:
            self.log(f"❌ 加载设置失败: {e}")


if __name__ == '__main__':
    app = TkDnD()
    gui = RealESRGAN_GUI_Enhanced(app)
    app.mainloop()
