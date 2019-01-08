import tkinter as tk
from tkinter import ttk
from pathlib import Path

from textarea import TextArea
from linegutter import LineGutter

SRC_PATH = Path(__file__).parent.parent
RESOURCES_PATH = SRC_PATH.joinpath("./resources/")


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        window_icon_path = RESOURCES_PATH.joinpath("icon.png").resolve()
        self.call("wm", "iconphoto", self._w, tk.Image("photo", file=window_icon_path))

        self.title("untitled — Codingg")

        self.text_area = TextArea(
            self,
            bg="#282c34",
            fg="#abb2bf",
            insertbackground="#528bff",
            borderwidth=0,
            undo=True
        )

        # TODO : reimplement the ttk style for scrollbar to give us more control
        self.scrollbar = ttk.Scrollbar(
            orient="vertical",
            command=self.scroll_text
        )

        self.text_area.configure(yscrollcommand=self.scrollbar.set)

        # line gutter
        self.line_gutter = LineGutter(
            self,
            self.text_area,
            bg="#282c34",
            fg="#4b5364",
            borderwidth=0,
            width=1
        )

        # status bar
        self.current_index = tk.StringVar()
        self.status_bar = tk.Text(self, bg="#21252b", fg="#9da5b4", borderwidth=0)
        self.status_bar_text = tk.Label(
            self.status_bar,
            bg=self.status_bar["bg"],
            fg=self.status_bar["fg"],
            textvar=self.current_index
        )

        # do element packing
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.status_bar_text.pack(side=tk.BOTTOM, fill=tk.X, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.line_gutter.pack(side=tk.LEFT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.bind_events()

    def bind_events(self):
        # scroll text area
        self.text_area.bind("<MouseWheel>", self.scroll_text)
        self.text_area.bind("<Button-4>", self.scroll_text)
        self.text_area.bind("<Button-5>", self.scroll_text)

        # update line gutter
        # self.text_area.bind("<KeyPress>", self.line_gutter.on_keypress)

        # disable scrolling and selection in line gutter
        self.line_gutter.bind("<MouseWheel>", lambda event: "break")
        self.line_gutter.bind("<Button-4>", lambda event: "break")
        self.line_gutter.bind("<Button-5>", lambda event: "break")

        # status bar events
        self.text_area.bind("<KeyRelease>", self.update_index)  # update line and column
        self.text_area.bind("<ButtonRelease-1>", self.update_index)

    def scroll_text(self, *args):
        if len(args) > 1:
            self.text_area.yview_moveto(args[1])
            self.line_gutter.yview_moveto(args[1])
        else:
            event = args[0]
            if event.delta:
                move = -1 * (event.delta / 120)
            else:
                if event.num == 5:
                    move = 1
                else:
                    move = -1

            self.text_area.yview_scroll(int(move), "units")
            self.line_gutter.yview_scroll(int(move), "units")

    def update_index(self, event=None):
        cursor_position = self.text_area.index(tk.INSERT)
        cursor_line, cursor_col = str(cursor_position).split(".")

        self.current_index.set(f"Ln {cursor_line}, Col {int(cursor_col) + 1}")


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
