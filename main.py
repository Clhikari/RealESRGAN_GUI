import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from main_window import MainWindow


class TkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    """支持拖拽的窗口类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


def main():
    """主函数"""
    app = TkDnD()
    gui = MainWindow(app)
    app.mainloop()


if __name__ == "__main__":
    main()
