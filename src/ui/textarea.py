import tkinter as tk


class TextArea(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)

        self.master = master

        self.config(wrap=tk.WORD)

        self.bind_events()

    def bind_events(self):
        self.bind("<Control-a>", self.select_all)
        self.bind("<Control-c>", self.copy)
        self.bind("<Control-v>", self.paste)
        self.bind("<Control-x>", self.cut)
        self.bind("<Control-y>", self.redo)
        self.bind("<Control-z>", self.undo)
        self.bind("<Control-g>", self.print_num_lines)
        # self.bind("<BackSpace>", self.on_key_backspace)

    def cut(self, event=None):
        self.event_generate("<<Cut>>")

    def copy(self, event=None):
        print("Fired")
        self.event_generate("<<Copy>>")

    def paste(self, event=None):
        self.event_generate("<<Paste>>")
        return "break"

    def undo(self, event=None):
        self.event_generate("<<Undo>>")
        return "break"  # used to prevent events already handled by the `Text` widget from firing

    def redo(self, event=None):
        self.event_generate("<<Redo>>")
        return "break"

    def select_all(self, event=None):
        self.tag_add("sel", 1.0, tk.END)

    def print_num_lines(self, event=None):
        final_index = str(self.index(tk.END))
        num_lines: str = final_index.split(".")[0]
        print(f"Number of lines: {int(num_lines) - 1}")
