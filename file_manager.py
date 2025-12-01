import os
import re
from tkinterdnd2 import DND_FILES


class FileManager:
    """管理选中的文件列表"""

    def __init__(self):
        self.selected_files = []

    def add_files(self, files):
        """添加文件到列表（去重）"""
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)

    def remove_file(self, file_path):
        """从列表中移除文件"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)

    def clear(self):
        """清空文件列表"""
        self.selected_files.clear()

    def get_count(self):
        """获取文件数量"""
        return len(self.selected_files)

    def get_files(self):
        """获取文件列表"""
        return self.selected_files

    @staticmethod
    def parse_dropped_files(data):
        """
        解析拖拽进来的文件路径字符串
        处理 Windows 路径的大括号问题
        """
        filepaths = []
        pattern = r"\{.*?\}|\S+"
        matches = re.findall(pattern, data)

        for match in matches:
            path = match.strip("{}")
            if os.path.isfile(path):
                if path.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff")
                ):
                    filepaths.append(path)

        return tuple(filepaths)

    @staticmethod
    def truncate_filename(filename, max_length=35):
        """
        截断过长的文件名
        例如: very_long_filename.jpg -> very_long...name.jpg
        """
        if len(filename) <= max_length:
            return filename

        head = 15
        tail = 15
        return filename[:head] + "..." + filename[-tail:]


class DragDropHelper:
    """拖拽功能辅助类"""

    @staticmethod
    def register_drag_drop(widget, drop_callback):
        """为CTk组件及其内部控件注册拖拽事件"""
        try:
            # 尝试直接注册（针对原生 tkinter 组件）
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", drop_callback)
        except AttributeError:
            # 如果是 CTk 组件，尝试注册其内部的核心控件
            if hasattr(widget, "_canvas"):
                widget._canvas.drop_target_register(DND_FILES)
                widget._canvas.dnd_bind("<<Drop>>", drop_callback)

            # 注册内部 Label (CTkLabel, CTkButton 的文字部分)
            if hasattr(widget, "_text_label"):
                widget._text_label.drop_target_register(DND_FILES)
                widget._text_label.dnd_bind("<<Drop>>", drop_callback)
            if hasattr(widget, "_label"):
                widget._label.drop_target_register(DND_FILES)
                widget._label.dnd_bind("<<Drop>>", drop_callback)

            # 递归注册所有子组件
            for child in widget.winfo_children():
                DragDropHelper.register_drag_drop(child, drop_callback)
