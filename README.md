## <div align="center"><b><a href="README.md">English</a> | <a href="README_CN.md">简体中文</a></b></div>

---

# A Simple Real-ESRGAN GUI Tool 🖼️

A graphical batch processing tool for `realesrgan-ncnn-vulkan.exe`.

![App Screenshot](.github\img\p1.png)

---

### 🤔 Why another wheel?

There are already many GUIs out there, so why make another one?

A: Frankly, the main reason is that I personally encountered a recurring issue with [TransparentLC/realesrgan-gui](https://github.com/TransparentLC/realesrgan-gui) where upscaled images would sometimes have black grid artifacts. The exact cause is still unknown to me.

So, I built this simpler version that directly calls the official command-line program, hoping to work around this problem.

### ⭐ Features

*   **🎯 Simple**: Focuses on the core batch processing functionality.
*   **⚙️ Implementation**: A direct wrapper for the official `ncnn-vulkan` program. The goal is to solve the black grid issue I encountered through the most direct method of execution.
*   **🎨 Custom magnification**: Enter the magnification factor you want in the input box; magnification can be increased to decimal levels.

This is a very minimalistic tool. In other aspects, it not be as feature-rich as other available GUIs.

### 🚀 Usage

1.  Download the `.exe` from this project's [Releases](https://github.com/Clhikari/SaveRealESRGAN_GUI/releases/tag/latest) page.
2.  Download `source code` from the official [Real-ESRGAN Releases](https://github.com/xinntao/Real-ESRGAN/releases) page.
3.  **Recommendation**: Place both `.exe` files in the same folder.
4.  Run the tool, select the path to the `.exe`, select your images, choose an output folder, and start processing.