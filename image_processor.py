import os
import re
import subprocess
from PIL import Image

class ImageProcessor:
    """处理图像超分辨率任务"""

    def __init__(self, logger=None):
        self.logger = logger
        self.current_process = None
        self.stop_event = False
        Image.MAX_IMAGE_PIXELS = None

    def log(self, message):
        """日志输出"""
        if self.logger:
            self.logger(message)

    def stop(self):
        """停止当前处理"""
        self.stop_event = True
        if self.current_process:
            try:
                self.current_process.kill()
                self.log("🛑 已强制终止当前子进程。")
            except Exception as e:
                self.log(f"⚠️ 终止进程时出错: {e}")

    def reset_stop_flag(self):
        """重置停止标志"""
        self.stop_event = False

    def build_command(self, exe_path, input_path, output_path, params):
        """构建处理命令"""
        command = [
            exe_path,
            "-i",
            input_path,
            "-o",
            output_path,
            "-n",
            params["model"],
            "-f",
            "png",  # 强制输出PNG以保真
        ]

        if params.get("tile_size") and params["tile_size"] != "0":
            command.extend(["-t", params["tile_size"]])

        if params.get("gpu_id") and params["gpu_id"].lower() != "auto":
            command.extend(["-g", params["gpu_id"]])

        if params.get("threads") and params["threads"] != "1:2:2":
            command.extend(["-j", params["threads"]])

        if params.get("tta"):
            command.append("-x")

        command.append("-v")
        return command

    def process_single_image(
        self, input_file, output_dir, params, progress_callback=None
    ):
        """
        处理单张图像

        Args:
            input_file: 输入文件路径
            output_dir: 输出目录
            params: 处理参数字典
            progress_callback: 进度回调函数 callback(percentage, filename)

        Returns:
            bool: 是否成功
        """
        filename = os.path.basename(input_file)
        base, ext = os.path.splitext(filename)

        # 临时PNG输出
        temp_png = f"temp_{base}_{params['suffix']}.png"
        temp_output_path = os.path.join(output_dir, temp_png)

        # 最终输出路径
        final_ext = self._get_output_extension(params["format"], ext)
        final_output = os.path.join(output_dir, f"{base}{params['suffix']}{final_ext}")

        # 获取原图尺寸
        try:
            with Image.open(input_file) as img:
                src_width, src_height = img.size
        except Exception as e:
            self.log(f"❌ 无法读取原图尺寸: {e}")
            return False

        scale_value = float(params["scale"])
        target_width = int(src_width * scale_value)
        target_height = int(src_height * scale_value)

        # 构建命令
        command = self.build_command(
            params["exe_path"], input_file, temp_output_path, params
        )

        # 如果放大为1直接跳转到转格式阶段
        if src_width == target_width and src_height == target_height:
            self.log(f"检测到放大倍数为1")
            self._post_process(
                input_file, final_output, target_width, target_height, params
            )
            self.log(f"✅ 成功: 已保存为 {os.path.basename(final_output)}")
            return True

        self.log(f"\n{'='*60}\n▶ 开始处理: {filename}\n{'='*60}")

        try:
            # 执行处理
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # 读取输出
            for line in iter(self.current_process.stdout.readline, ""):
                if self.stop_event:
                    self.current_process.kill()
                    return False

                if line:
                    stripped_line = line.strip()
                    self.log(stripped_line)

                    # 提取进度
                    percentage_match = re.search(r"(\d+\.?\d*)%", stripped_line)
                    if percentage_match and progress_callback:
                        try:
                            percentage = float(percentage_match.group(1))
                            progress_callback(percentage, filename)
                        except ValueError:
                            pass

            self.current_process.stdout.close()
            return_code = self.current_process.wait()
            self.current_process = None

            if self.stop_event:
                return False

            # 后处理
            if return_code == 0 and os.path.exists(temp_output_path):
                success = self._post_process(
                    temp_output_path, final_output, target_width, target_height, params
                )

                # 清理临时文件
                if os.path.exists(temp_output_path):
                    try:
                        os.remove(temp_output_path)
                    except:
                        pass

                if success:
                    self.log(f"✅ 成功: 已保存为 {os.path.basename(final_output)}")
                    return True

            self.log(f"❌ 处理失败或未生成临时文件")
            return False

        except FileNotFoundError:
            self.log(f"❌ 致命错误: 未找到可执行文件 '{params['exe_path']}'")
            return False
        except Exception as e:
            self.log(f"❌ 发生意外错误: {e}")
            return False

    def _get_output_extension(self, format_choice, original_ext):
        """获取输出文件扩展名"""
        format_map = {
            "保持原格式": original_ext,
            "PNG": ".png",
            "JPEG": ".jpg",
            "WebP": ".webp",
            "BMP": ".bmp",
            "TIFF": ".tiff",
        }
        return format_map.get(format_choice, original_ext)

    def _post_process(self, temp_path, final_path, target_w, target_h, params):
        """后处理: Resize + 格式转换 + 压缩"""
        quality = int(params.get("quality", 95))
        self.log("⚙️ 正在进行后期处理...")
        try:
            with Image.open(temp_path) as img:
                # Resize
                if img.width != target_w or img.height != target_h:
                    self.log(
                        f"🔄 调整尺寸: {img.width}x{img.height} → {target_w}x{target_h}"
                    )
                    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

                # 保存参数
                save_kwargs = {}
                ext_lower = os.path.splitext(final_path)[1].lower()

                # 确定PIL格式
                if ".jpg" in ext_lower or ".jpeg" in ext_lower:
                    self.log(f"压缩 (质量: {quality})...")
                    pil_format = "JPEG"
                    save_kwargs["quality"] = quality
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                elif ".webp" in ext_lower:
                    self.log(f"压缩 (质量: {quality})...")
                    pil_format = "WEBP"
                    save_kwargs["quality"] = quality
                elif ".png" in ext_lower:
                    pil_format = "PNG"
                elif ".bmp" in ext_lower:
                    pil_format = "BMP"
                elif ".tiff" in ext_lower:
                    pil_format = "TIFF"
                else:
                    pil_format = None

                # 保存
                img.save(final_path, format=pil_format, **save_kwargs)

            return True
        except Exception as e:
            self.log(f"❌ 后期处理失败: {e}")
            return False
