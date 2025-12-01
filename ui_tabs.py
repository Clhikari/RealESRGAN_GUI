import customtkinter as ctk
from ui_components import UIBuilder
from file_manager import DragDropHelper


class BasicSettingsTab:
    """基础设置标签页"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window

        # 创建滚动容器
        self.scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # 创建UI组件
        self.create_config_section()
        self.create_params_section()
        self.create_files_section()
        self.create_control_section()
        self.create_log_section()

    def create_config_section(self):
        """创建基础配置区域"""
        card = UIBuilder.create_card(self.scroll_frame, "⚙️ 基础配置")
        card.pack(fill="x", pady=(0, 15))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))

        # 可执行文件
        self.exe_path = ctk.StringVar()
        UIBuilder.create_file_picker(
            content,
            "📂 可执行文件",
            self.exe_path,
            self.main_window.browse_exe,
            "选择 EXE",
        )

        # 输出文件夹
        self.output_folder_path = ctk.StringVar()
        UIBuilder.create_file_picker(
            content,
            "📁 输出文件夹",
            self.output_folder_path,
            self.main_window.browse_output_folder,
            "选择文件夹",
        )

    def create_params_section(self):
        """创建参数设置区域"""
        card = UIBuilder.create_card(self.scroll_frame, "🎯 参数设置")
        card.pack(fill="x", pady=(0, 15))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))

        # 第一行: 模型和后缀
        row1 = ctk.CTkFrame(content, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        # 模型选择
        model_container, model_frame = UIBuilder.create_param_card(row1, "模型", "🎯")
        model_container.pack(side="left", fill="x", expand=True, padx=(0, 7))

        self.model_name = ctk.StringVar(value="realesrgan-x4plus-anime")
        UIBuilder.create_combobox(
            model_frame,
            self.model_name,
            [
                "realesrgan-x4plus",
                "realesrnet-x4plus",
                "realesrgan-x4plus-anime",
                "realesr-animevideov3",
            ],
        ).pack(fill="x", padx=15, pady=(0, 10))

        # 输出后缀
        suffix_container, suffix_frame = UIBuilder.create_param_card(
            row1, "输出后缀", "✏️"
        )
        suffix_container.pack(side="left", fill="x", expand=True, padx=(7, 0))

        self.suffix = ctk.StringVar(value="_upscaled")
        ctk.CTkEntry(
            suffix_frame, textvariable=self.suffix, corner_radius=8, height=32
        ).pack(fill="x", padx=15, pady=(0, 10))

        # 第二行: 放大倍数和输出格式
        row2 = ctk.CTkFrame(content, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        # 放大倍数
        scale_container, scale_frame = UIBuilder.create_param_card(
            row2, "放大倍数", "🔍"
        )
        scale_container.pack(side="left", fill="x", expand=True, padx=(0, 7))

        self.scale_ratio = ctk.StringVar(value="4.0")
        ctk.CTkEntry(
            scale_frame,
            textvariable=self.scale_ratio,
            corner_radius=8,
            height=32,
            placeholder_text="例如: 2.0, 2.5, 4.0",
        ).pack(fill="x", padx=15, pady=(0, 10))

        # 输出格式
        format_container, format_frame = UIBuilder.create_param_card(
            row2, "输出格式", "🖼️"
        )
        format_container.pack(side="left", fill="x", expand=True, padx=(7, 0))

        self.output_format = ctk.StringVar(value="保持原格式")
        UIBuilder.create_combobox(
            format_frame,
            self.output_format,
            ["保持原格式", "PNG", "JPEG", "WebP", "BMP", "TIFF"],
        ).pack(fill="x", padx=15, pady=(0, 10))

        # 压缩质量
        quality_container, quality_frame = UIBuilder.create_param_card(
            content, "压缩质量", "⚡"
        )
        quality_container.pack(fill="x", padx=(0, 0))

        self.quality_value = ctk.IntVar(value=95)
        self.quality_slider, self.quality_label = UIBuilder.create_slider_with_label(
            quality_frame, self.quality_value, 10, 100, self.update_quality_label
        )
        self.quality_label.configure(text="95")

    def create_files_section(self):
        """创建文件选择区域"""
        card = UIBuilder.create_card(self.scroll_frame, "🖼️ 图片文件")
        card.pack(fill="x", pady=(0, 15))

        files_inner = ctk.CTkFrame(card, fg_color="transparent")
        files_inner.pack(fill="x", padx=15, pady=(0, 15))

        # 文件状态显示
        self.files_selected_status = ctk.StringVar(value="未选择任何文件")
        status_frame = ctk.CTkFrame(
            files_inner, fg_color="#2a2a2d", corner_radius=8, height=50
        )
        status_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        status_frame.pack_propagate(False)

        # 注册拖拽
        DragDropHelper.register_drag_drop(status_frame, self.main_window.drop_files)
        DragDropHelper.register_drag_drop(files_inner, self.main_window.drop_files)

        self.status_icon = ctk.CTkLabel(
            status_frame, text="⚪", font=ctk.CTkFont(size=20)
        )
        self.status_icon.pack(side="left", padx=15)
        DragDropHelper.register_drag_drop(self.status_icon, self.main_window.drop_files)

        self.files_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.files_selected_status,
            font=ctk.CTkFont(size=13),
        )
        self.files_label.pack(side="left", fill="x", expand=True)
        DragDropHelper.register_drag_drop(self.files_label, self.main_window.drop_files)

        # 选择按钮
        self.select_files_btn = ctk.CTkButton(
            files_inner,
            text="选择图片",
            command=self.main_window.browse_files,
            corner_radius=8,
            height=50,
            width=120,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=UIBuilder.PRIMARY_COLOR,
            hover_color="#1557c0",
        )
        self.select_files_btn.pack(side="left", padx=(0, 10))

        # 管理按钮
        self.manage_btn = ctk.CTkButton(
            files_inner,
            text="📋",
            command=self.main_window.open_file_manager,
            corner_radius=8,
            height=50,
            width=50,
            font=ctk.CTkFont(size=20),
            fg_color="#3a3a3d",
            hover_color="#4a4a4d",
        )
        self.manage_btn.pack(side="left")

    def create_control_section(self):
        """创建处理控制区域"""
        card = UIBuilder.create_card(self.scroll_frame, "🚀 处理控制")
        card.pack(fill="x", pady=(0, 15))

        control_inner = ctk.CTkFrame(card, fg_color="transparent")
        control_inner.pack(fill="x", padx=15, pady=(0, 15))

        # 停止按钮
        self.stop_button = ctk.CTkButton(
            control_inner,
            text="⏹ 停止处理",
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            state="disabled",
            command=self.main_window.stop_processing,
        )
        self.stop_button.pack(fill="x", pady=(0, 10))

        # 开始按钮
        self.start_button = ctk.CTkButton(
            control_inner,
            text="▶ 开始处理",
            command=self.main_window.start_processing_thread,
            corner_radius=10,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=UIBuilder.SUCCESS_COLOR,
            hover_color="#2b8a3e",
        )
        self.start_button.pack(fill="x", pady=(0, 15))

        # 进度条
        progress_frame = ctk.CTkFrame(control_inner, fg_color="transparent")
        progress_frame.pack(fill="x")

        self.progress = ctk.CTkProgressBar(
            progress_frame,
            corner_radius=8,
            height=20,
            progress_color=UIBuilder.PRIMARY_COLOR,
        )
        self.progress.pack(fill="x", pady=(0, 8))
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="💡 欢迎使用!请选择文件和配置参数",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
        )
        self.status_label.pack(anchor="w")

    def create_log_section(self):
        """创建日志区域"""
        card = UIBuilder.create_card(self.scroll_frame, "📋 处理日志")
        card.pack(fill="both", expand=True)

        self.log_area = UIBuilder.create_textbox(card)
        self.log_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_area.configure(state="disabled")

    def update_quality_label(self, value):
        """更新质量滑块标签"""
        self.quality_label.configure(text=str(int(float(value))))

    def get_settings_dict(self):
        """获取设置字典"""
        return {
            "exe_path": self.exe_path.get(),
            "output_folder": self.output_folder_path.get(),
            "model": self.model_name.get(),
            "suffix": self.suffix.get(),
            "scale": self.scale_ratio.get(),
            "format": self.output_format.get(),
            "compression": str(self.quality_value.get()),
        }

    def load_from_dict(self, settings):
        """从字典加载设置"""
        self.exe_path.set(settings.get("exe_path", ""))
        self.output_folder_path.set(settings.get("output_folder", ""))
        self.model_name.set(settings.get("model", "realesrgan-x4plus-anime"))
        self.suffix.set(settings.get("suffix", "_upscaled"))
        self.scale_ratio.set(settings.get("scale", "4.0"))
        self.output_format.set(settings.get("format", "保持原格式"))
        self.quality_value.set(int(settings.get("compression", "95")))
        self.update_quality_label(self.quality_value.get())


class AdvancedSettingsTab:
    """高级设置标签页"""

    def __init__(self, parent):
        self.parent = parent

        # 创建滚动容器
        self.scroll_frame = ctk.CTkScrollableFrame(parent)
        self.scroll_frame.pack(fill="both", expand=True)

        # 创建UI组件
        self.create_gpu_section()
        self.create_performance_section()
        self.create_info_section()

    def create_gpu_section(self):
        """创建GPU设置区域"""
        card = UIBuilder.create_card(self.scroll_frame, "🎮 GPU 设置")
        card.pack(fill="x", pady=(0, 15))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))

        # GPU ID
        self.gpu_id = ctk.StringVar(value="auto")
        UIBuilder.create_labeled_entry(content, "🎮 GPU ID", self.gpu_id)[1].configure(
            placeholder_text="auto/0/1/2 或多GPU: 0,1,2"
        )

        # Tile Size
        tile_frame = ctk.CTkFrame(content, fg_color="transparent")
        tile_frame.pack(fill="x")

        ctk.CTkLabel(
            tile_frame,
            text="🔲 Tile Size",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w",
        ).pack(side="left", padx=(0, 10))

        self.tile_size = ctk.StringVar(value="0")
        ctk.CTkEntry(
            tile_frame,
            textvariable=self.tile_size,
            corner_radius=8,
            height=35,
            placeholder_text="0=自动,或设置固定值(≥32)",
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            tile_frame,
            text="💡 显存不足时降低此值",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
        ).pack(side="left")

    def create_performance_section(self):
        """创建性能优化区域"""
        card = UIBuilder.create_card(self.scroll_frame, "⚡ 性能优化")
        card.pack(fill="x", pady=(0, 15))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))

        # 线程设置
        thread_frame = ctk.CTkFrame(content, fg_color="transparent")
        thread_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            thread_frame,
            text="⚙️ 线程数",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w",
        ).pack(side="left", padx=(0, 10))

        self.thread_count = ctk.StringVar(value="1:2:2")
        ctk.CTkEntry(
            thread_frame,
            textvariable=self.thread_count,
            corner_radius=8,
            height=35,
            placeholder_text="格式: load:proc:save",
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            thread_frame,
            text="💡 默认 1:2:2",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
        ).pack(side="left")

        # TTA 模式
        tta_frame = ctk.CTkFrame(content, fg_color="#2a2a2d", corner_radius=10)
        tta_frame.pack(fill="x")

        tta_inner = ctk.CTkFrame(tta_frame, fg_color="transparent")
        tta_inner.pack(fill="x", padx=15, pady=15)

        self.enable_tta = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            tta_inner,
            text="✨ 启用 TTA 模式(更高质量,处理更慢)",
            variable=self.enable_tta,
            onvalue=True,
            offvalue=False,
            progress_color=UIBuilder.PRIMARY_COLOR,
            button_color=UIBuilder.PRIMARY_COLOR,
            button_hover_color="#1557c0",
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w")

    def create_info_section(self):
        """创建说明区域"""
        card = UIBuilder.create_card(self.scroll_frame, "📖 参数说明")
        card.pack(fill="both", expand=True)

        info_text = UIBuilder.create_textbox(card, height=200)
        info_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        info_content = """📚 参数详细说明:

            🎮 GPU ID:
            • auto - 自动选择最佳GPU
            • 0/1/2 - 指定单个GPU
            • 0,1,2 - 使用多个GPU并行处理

            🔲 Tile Size:
            • 0 - 自动计算(推荐)
            • 固定值 - 手动设置(如256、512)
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
            • 推理时间大幅增加,质量提升微乎其微不建议开启"""

        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")

    def get_settings_dict(self):
        """获取设置字典"""
        return {
            "gpu_id": self.gpu_id.get(),
            "tile_size": self.tile_size.get(),
            "threads": self.thread_count.get(),
            "tta": str(self.enable_tta.get()),
        }

    def load_from_dict(self, settings):
        """从字典加载设置"""
        self.gpu_id.set(settings.get("gpu_id", "auto"))
        self.tile_size.set(settings.get("tile_size", "0"))
        self.thread_count.set(settings.get("threads", "1:2:2"))
        self.enable_tta.set(settings.get("tta", "False") == "True")
