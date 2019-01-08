import tkinter as tk


class LineGutter(tk.Text):
    def __init__(self, master, text_area, **kwargs):
        super().__init__(master, **kwargs)

        self.text_area = text_area

        self.insert(1.0, "1")
        self.configure(state="disabled")

        self.bind_events()

    def bind_events(self):
        self.text_area.bind("<Return>", self.on_key_return)
        # TODO : add event to remove lines
        self.text_area.bind("<BackSpace>", self.on_key_backspace)

    def on_key_return(self, event=None):
        final_index = str(self.text_area.index(tk.END))
        num_lines: str = final_index.split(".")[0]

        line_nums_str = "\n".join(
            f"{no + 1}" for no in range(int(num_lines))
        )

        width = len(num_lines)
        self.configure(state="normal", width=width)
        self.delete(1.0, tk.END)
        self.insert(1.0, line_nums_str)
        self.configure(state="disabled")

    def on_key_backspace(self, event=None):
        pass
