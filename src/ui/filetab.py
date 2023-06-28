import tkinter as tk
from tkinter import ttk


class FileTab(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.text_area = None
        self.line_gutter = None
        self.scrollbar = None

        # Import the Notebook.tab element from the default theme
        self.style = ttk.Style()
        try:
            self.style.element_create("TNotebook.Tab", "from", "default")
        except tk.TclError:
            # gg.TNotebook.tab already exists
            pass

        # Redefine the TNotebook Tab layout to use the new element
        # fmt: off

        self.style.layout("CustomNotebook.Tab",
            [('CustomNotebook.Tab', {'children':
                [('CustomNotebook.padding', {'side': 'top', 'children':
                    [('CustomNotebook.focus', {'side': 'top', 'children':
                        [
                            ('CustomNotebook.label', {'side': 'left', 'sticky': ''}),
                            ("CustomNotebook.close", {"side": "left", "sticky": ""},),
                        ],
                    'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})])
        self.style.configure("CustomNotebook", background="#282c34", borderwidth=0)
        self.style.configure("CustomNotebook.Tab", background="#282c34", foreground="#abb2bf", borderwidth=2)
        self.style.configure("TFrame", background="#282c34", foreground="#282c34", borderwidth=0)
        self.style.map("CustomNotebook.Tab", background=[("selected", "green"), ("disabled", "red")])
        # fmt: on
