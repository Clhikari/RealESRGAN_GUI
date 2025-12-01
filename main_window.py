import os
import customtkinter as ctk
import pywinstyles
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from config_manager import ConfigManager
from image_processor import ImageProcessor
from file_manager import FileManager
from ui_components import UIBuilder, AnimationHelper
from ui_tabs import BasicSettingsTab, AdvancedSettingsTab


class MainWindow:
    """Real-ESRGAN GUI 主窗口"""

    def __init__(self, master):
        self.master = master
        self.setup_window()

        # 初始化模块
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.image_processor = ImageProcessor(logger=self.log)
        # 状态变量
        self.is_processing = False
        self.current_image_index = 0
        self.total_images = 0

        # 构建UI
        self.create_ui()

        # 加载配置
        self.load_settings()

        # 绑定关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """设置窗口基本属性"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.master.title("Real-ESRGAN工具")
        self.master.geometry("750x750")
        self.master.resizable(True, True)

        # 应用毛玻璃效果
        try:
            pywinstyles.apply_style(self.master, style="mica")
        except Exception as e:
            print(f"应用窗口特效失败: {e}")

    def create_ui(self):
        """创建主界面"""
        # 主容器
        main_container = ctk.CTkFrame(self.master, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题栏
        self.create_header(main_container)

        # 标签页
        self.create_tabview(main_container)

    def create_header(self, parent):
        """创建标题栏"""
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            title_frame,
            text="🎨 Real-ESRGAN 图像超分辨率处理",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="批量高质量图像放大工具",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
        ).pack(side="left", padx=15)

    def create_tabview(self, parent):
        """创建标签页视图"""
        self.tabview = ctk.CTkTabview(parent, corner_radius=15)
        self.tabview.pack(fill="both", expand=True)

        # 设置标签页样式
        self.tabview._segmented_button.configure(
            fg_color="#2a2a2d",
            selected_color=UIBuilder.PRIMARY_COLOR,
            selected_hover_color="#1557c0",
        )

        # 创建基础设置页
        self.basic_tab = BasicSettingsTab(self.tabview.add("基础设置"), self)

        # 创建高级设置页
        self.advanced_tab = AdvancedSettingsTab(self.tabview.add("高级设置"))

    def browse_exe(self):
        """选择可执行文件"""
        file = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if file:
            self.basic_tab.exe_path.set(file)
            self.log(f"✅ 已选择可执行文件: {os.path.basename(file)}")

    def browse_output_folder(self):
        """选择输出文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.basic_tab.output_folder_path.set(folder)
            self.log(f"✅ 已选择输出文件夹: {folder}")

    def browse_files(self):
        """选择图片文件"""
        files = filedialog.askopenfilenames(
            title="选择图片", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if files:
            self.file_manager.add_files(list(files))
            self.update_file_status()

    def drop_files(self, event):
        """处理拖拽释放事件"""
        files = FileManager.parse_dropped_files(event.data)
        if files:
            self.file_manager.add_files(list(files))
            self.update_file_status()
        else:
            self.log("⚠️ 拖拽的文件无效或不是支持的图片格式")

    def update_file_status(self):
        """更新文件状态显示"""
        count = self.file_manager.get_count()
        if count == 0:
            self.basic_tab.files_selected_status.set("未选择任何文件 (支持拖拽)")
            self.basic_tab.status_icon.configure(text="⚪")
        else:
            self.basic_tab.files_selected_status.set(f"已选择 {count} 个文件")
            self.basic_tab.status_icon.configure(text="✅")
            self.log(f"📂 当前文件列表共 {count} 个文件")

    def open_file_manager(self):
        """打开文件管理弹窗"""
        if not self.file_manager.get_count():
            self.log("⚠️ 列表为空,无需管理")
            return

        from file_manager_dialog import FileManagerDialog

        FileManagerDialog(self.master, self.file_manager, self.update_file_status, self.log)

    def start_processing_thread(self):
        """启动处理线程"""
        self.basic_tab.start_button.configure(state="disabled", text="⏳ 处理中...")
        AnimationHelper.animate_button_click(self.basic_tab.start_button)

        # 清空日志
        self.basic_tab.log_area.configure(state="normal")
        self.basic_tab.log_area.delete("1.0", tk.END)
        self.basic_tab.log_area.configure(state="disabled")

        # 重置进度
        self.basic_tab.progress.set(0)

        # 启动线程
        self.processing_thread = Thread(target=self.process_images, daemon=True)
        self.processing_thread.start()

    def stop_processing(self):
        """停止处理"""
        if not self.is_processing:
            return

        self.log("🛑 正在尝试停止任务...")
        self.image_processor.stop()

    def process_images(self):
        """批量处理图像"""
        # 收集参数
        params = {
            "exe_path": self.basic_tab.exe_path.get(),
            "model": self.basic_tab.model_name.get(),
            "suffix": self.basic_tab.suffix.get(),
            "scale": self.basic_tab.scale_ratio.get(),
            "format": self.basic_tab.output_format.get(),
            "quality": self.basic_tab.quality_value.get(),
            "gpu_id": self.advanced_tab.gpu_id.get(),
            "tile_size": self.advanced_tab.tile_size.get(),
            "threads": self.advanced_tab.thread_count.get(),
            "tta": self.advanced_tab.enable_tta.get(),
        }

        output_dir = self.basic_tab.output_folder_path.get()
        files = self.file_manager.get_files()

        # 验证输入
        if not all(
            [os.path.isfile(params["exe_path"]), files, os.path.isdir(output_dir)]
        ):
            self._update_error_status()
            return

        # 开始处理
        self.image_processor.reset_stop_flag()
        self.is_processing = True
        self._update_ui_processing_state(True)

        self.total_images = len(files)
        success_count = 0

        for i, input_file in enumerate(files):
            if self.image_processor.stop_event:
                self.log("⚠️ 用户已取消后续任务。")
                break

            self.current_image_index = i + 1

            # 处理单张图片
            success = self.image_processor.process_single_image(
                input_file,
                output_dir,
                params,
                progress_callback=self.update_progress_from_percentage,
            )

            if success:
                success_count += 1

        # 完成
        self.is_processing = False
        self._update_ui_processing_state(False)
        self._update_completion_status(success_count)

        AnimationHelper.animate_progress_completion(self.basic_tab.progress)
        self.log(
            f"\n{'='*60}\n🎉 批量处理完成!\n✅ 成功: {success_count}/{self.total_images}\n{'='*60}"
        )

    def update_progress_from_percentage(self, percentage, filename):
        """更新处理进度"""
        single_weight = 1.0 / self.total_images
        previous = (self.current_image_index - 1) / self.total_images
        current = (percentage / 100.0) * single_weight
        total = previous + current

        def _update():
            self.basic_tab.progress.set(total)
            self.basic_tab.status_label.configure(
                text=f"🔄 正在处理: {filename} - {percentage:.1f}% ({self.current_image_index}/{self.total_images})",
                text_color="white",
            )

        self.master.after(0, _update)

    def _update_error_status(self):
        """更新错误状态"""

        def _update():
            self.basic_tab.status_label.configure(
                text="❌ 错误: 请检查所有路径和文件选择是否正确",
                text_color=UIBuilder.ERROR_COLOR,
            )
            self.basic_tab.start_button.configure(state="normal", text="▶ 开始处理")

        self.master.after(0, _update)

    def _update_ui_processing_state(self, processing):
        """更新UI处理状态"""

        def _update():
            if processing:
                self.basic_tab.start_button.configure(
                    state="disabled", text="⏳ 处理中..."
                )
                self.basic_tab.stop_button.configure(state="normal")
            else:
                self.basic_tab.start_button.configure(state="normal", text="▶ 开始处理")
                self.basic_tab.stop_button.configure(state="disabled")

        self.master.after(0, _update)

    def _update_completion_status(self, success_count):
        """更新完成状态"""

        def _update():
            if self.image_processor.stop_event:
                text = "⛔ 任务已停止"
                color = "orange"
            else:
                text = f"✨ 全部完成! 成功: {success_count}/{self.total_images}"
                color = "green"

            self.basic_tab.status_label.configure(text=text, text_color=color)
            self.basic_tab.progress.set(1.0)

        self.master.after(0, _update)

    def log(self, message):
        """日志输出"""

        def _update():
            self.basic_tab.log_area.configure(state="normal")
            self.basic_tab.log_area.insert(tk.END, message + "\n")
            self.basic_tab.log_area.see(tk.END)
            self.basic_tab.log_area.configure(state="disabled")

        self.master.after(0, _update)

    def load_settings(self):
        """加载配置"""
        settings = self.config_manager.load_settings()
        if not settings:
            self.log("💡 未找到配置文件,将使用默认设置。")
            return

        try:
            self.basic_tab.load_from_dict(settings)
            self.advanced_tab.load_from_dict(settings)
            self.log("⚙️ 设置已加载。")
        except Exception as e:
            self.log(f"❌ 加载设置失败: {e}")

    def save_settings(self):
        """保存配置"""
        settings = {}
        settings.update(self.basic_tab.get_settings_dict())
        settings.update(self.advanced_tab.get_settings_dict())

        try:
            self.config_manager.save_settings(settings)
            self.log("⚙️ 设置已保存。")
        except Exception as e:
            self.log(f"❌ 保存设置失败: {e}")

    def on_closing(self):
        """窗口关闭事件"""
        self.save_settings()
        self.master.destroy()
