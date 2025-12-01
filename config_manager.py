import os
import sys
import configparser


class ConfigManager:
    """处理应用程序配置的加载和保存"""

    def __init__(self, config_filename="config.ini"):
        self.config = configparser.ConfigParser()
        self.settings_file = os.path.join(self.get_app_path(), config_filename)

    @staticmethod
    def get_app_path():
        """获取应用程序路径"""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def load_settings(self):
        """加载配置文件"""
        if not os.path.exists(self.settings_file):
            return None

        try:
            self.config.read(self.settings_file, encoding="utf-8")
            return dict(self.config["DEFAULT"])
        except Exception as e:
            raise Exception(f"加载配置失败: {e}")

    def save_settings(self, settings_dict):
        """保存配置到文件"""
        try:
            self.config["DEFAULT"] = settings_dict
            with open(self.settings_file, "w", encoding="utf-8") as f:
                self.config.write(f)
        except Exception as e:
            raise Exception(f"保存配置失败: {e}")

    def get_default_settings(self):
        """返回默认配置"""
        return {
            "exe_path": "",
            "output_folder": "",
            "model": "realesrgan-x4plus-anime",
            "suffix": "_upscaled",
            "scale": "4.0",
            "format": "保持原格式",
            "compression": "95",
            "gpu_id": "auto",
            "tile_size": "0",
            "threads": "1:2:2",
            "tta": "False",
        }
