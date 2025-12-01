import os
import customtkinter as ctk
from file_manager import FileManager
from ui_components import UIBuilder


class FileManagerDialog:
    """文件列表管理弹窗"""

    def __init__(self, parent, file_manager, update_callback, logger=None):
        self.logger = logger
        self.file_manager = file_manager
        self.update_callback = update_callback
        # 创建弹窗
        self.top = ctk.CTkToplevel(parent)
        self.top.title("文件列表管理")
        self.top.geometry("500x400")
        self.top.transient(parent)
        self.top.grab_set()

        self.create_ui()

    def log(self, message):
        """日志输出"""
        if self.logger:
            self.logger(message)

    def create_ui(self):
        """创建UI"""
        # 标题栏
        header = ctk.CTkFrame(self.top, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text=f"已选文件 ({self.file_manager.get_count()})",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="清空全部",
            width=80,
            height=30,
            fg_color=UIBuilder.ERROR_COLOR,
            hover_color="#c62828",
            command=self.clear_all,
        ).pack(side="right")

        # 滚动列表区域
        self.scroll_frame = ctk.CTkScrollableFrame(self.top)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 渲染列表
        self.render_file_list()

    def render_file_list(self):
        """渲染文件列表"""
        # 清空现有显示
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        files = self.file_manager.get_files()

        for i, file_path in enumerate(files):
            # 创建每一行的容器
            row = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b")
            row.pack(fill="x", pady=2)

            # 删除按钮
            del_btn = ctk.CTkButton(
                row,
                text="❌",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#404040",
                text_color="#ff5555",
                command=lambda f=file_path: self.remove_file(f),
            )
            del_btn.pack(side="right", padx=5)

            # 文件名标签
            filename = os.path.basename(file_path)
            display_name = FileManager.truncate_filename(filename)

            label = ctk.CTkLabel(row, text=f"{i+1}. {display_name}", anchor="w")
            label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

    def remove_file(self, file_path):
        """移除文件"""
        self.file_manager.remove_file(file_path)
        self.update_callback()

        # 如果删完了,关闭窗口
        if self.file_manager.get_count() == 0:
            self.top.destroy()
        else:
            # 重新渲染列表
            self.render_file_list()
            # 更新标题
            self.update_header_count()

    def clear_all(self):
        """清空所有文件"""
        self.file_manager.clear()
        self.update_callback()
        self.top.destroy()
        self.log(f"❌已移除全部文件")

    def update_header_count(self):
        """更新标题栏数量"""
        for widget in self.top.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(
                            text=f"已选文件 ({self.file_manager.get_count()})"
                        )
                        break
                break
