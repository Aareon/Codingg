import tkinter as tk
from tkinter import ttk


class FileTab(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.text_area = None
        self.line_gutter = None
        self.scrollbar = None

        # Import the Notebook.tab element from the default theme
        self.styler = ttk.Style()
        try:
            self.styler.element_create("TNotebook.Tab", "from", "default")
        except tk.TclError:
            # gg.TNotebook.tab already exists
            pass

        # Redefine the TNotebook Tab layout to use the new element
        # fmt: off
        self.styler.layout("TNotebook.Tab",
            [('TNotebook.Tab', {'children':
                [('TNotebook.padding', {'side': 'top', 'children':
                    [('TNotebook.focus', {'side': 'top', 'children':
                        [('TNotebook.label', {'side': 'top', 'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})])
        self.styler.configure("TNotebook", background="#282c34", borderwidth=0)
        self.styler.configure("TNotebook.Tab", background="#282c34", foreground="#abb2bf", borderwidth=2)
        self.styler.configure("TFrame", background="#282c34", foreground="#282c34", borderwidth=0)
        self.styler.map("TNotebook.Tab", background=[("selected", "green"), ("disabled", "red")])
        # fmt: on
