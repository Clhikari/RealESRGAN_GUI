import customtkinter as ctk
import tkinter as tk


class UIBuilder:
    """UI组件构建辅助类"""

    # 颜色主题
    PRIMARY_COLOR = "#1f6feb"
    SUCCESS_COLOR = "#2ea043"
    WARNING_COLOR = "#d29922"
    ERROR_COLOR = "#f85149"
    CARD_BG = "#1c1c1e"

    @staticmethod
    def create_card(parent, title):
        """创建卡片容器"""
        card = ctk.CTkFrame(parent, fg_color=UIBuilder.CARD_BG, corner_radius=15)

        title_label = ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(15, 10))

        return card

    @staticmethod
    def create_labeled_entry(parent, label_text, var, width=120):
        """创建带标签的输入框"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=width,
            anchor="w",
        ).pack(side="left", padx=(0, 10))

        entry = ctk.CTkEntry(frame, textvariable=var, corner_radius=8, height=35)
        entry.pack(side="left", fill="x", expand=True)

        return frame, entry

    @staticmethod
    def create_file_picker(parent, label_text, var, command, button_text="选择"):
        """创建文件/文件夹选择器"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            anchor="w",
        ).pack(side="left", padx=(0, 10))

        ctk.CTkEntry(frame, textvariable=var, corner_radius=8, height=35).pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )

        ctk.CTkButton(
            frame,
            text=button_text,
            command=command,
            corner_radius=8,
            width=120,
            fg_color="#404044",
            hover_color="#505054",
        ).pack(side="left")

        return frame

    @staticmethod
    def create_param_card(parent, title, icon):
        """创建参数卡片容器"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        frame = ctk.CTkFrame(container, fg_color="#2a2a2d", corner_radius=10)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame, text=f"{icon} {title}", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        return container, frame

    @staticmethod
    def create_combobox(parent, variable, values, **kwargs):
        """创建下拉框"""
        combo = ctk.CTkComboBox(
            parent,
            variable=variable,
            values=values,
            state="readonly",
            corner_radius=8,
            button_color=UIBuilder.PRIMARY_COLOR,
            button_hover_color="#1557c0",
            dropdown_fg_color="#2a2a2d",
            dropdown_hover_color="#3a3a3d",
            dropdown_text_color="white",
            **kwargs,
        )
        return combo

    @staticmethod
    def create_slider_with_label(parent, variable, from_, to, command, label_var=None):
        """创建带数值显示的滑块"""
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=(0, 10))

        if label_var is None:
            label_var = ctk.IntVar(value=variable.get())

        label = ctk.CTkLabel(
            inner,
            textvariable=label_var,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=UIBuilder.PRIMARY_COLOR,
            width=30,
        )
        label.pack(side="right", padx=(5, 0))

        slider = ctk.CTkSlider(
            inner,
            from_=from_,
            to=to,
            number_of_steps=int(to - from_),
            variable=variable,
            command=command,
            button_color=UIBuilder.PRIMARY_COLOR,
            button_hover_color="#1557c0",
            progress_color=UIBuilder.PRIMARY_COLOR,
        )
        slider.pack(side="left", fill="x", expand=True)

        return slider, label

    @staticmethod
    def create_textbox(parent, **kwargs):
        """创建文本框"""
        defaults = {
            "wrap": tk.WORD,
            "corner_radius": 10,
            "font": ctk.CTkFont(family="Consolas", size=11),
            "fg_color": "#1a1a1c",
        }
        defaults.update(kwargs)

        textbox = ctk.CTkTextbox(parent, **defaults)
        return textbox


class AnimationHelper:
    """动画效果辅助类"""

    @staticmethod
    def animate_button_click(button, original_height=45):
        """按钮点击动画 - 缩放效果"""

        def scale_down():
            button.configure(height=original_height - 5)
            button.master.after(50, scale_up)

        def scale_up():
            button.configure(height=original_height)

        scale_down()

    @staticmethod
    def animate_progress_completion(progress_bar, colors=None):
        """进度条完成动画 - 闪烁效果"""
        if colors is None:
            colors = [
                UIBuilder.PRIMARY_COLOR,
                UIBuilder.SUCCESS_COLOR,
                UIBuilder.PRIMARY_COLOR,
                UIBuilder.SUCCESS_COLOR,
            ]

        def flash(step=0):
            if step < len(colors):
                progress_bar.configure(progress_color=colors[step])
                progress_bar.master.after(150, lambda: flash(step + 1))
            else:
                progress_bar.configure(progress_color=UIBuilder.SUCCESS_COLOR)

        flash()
