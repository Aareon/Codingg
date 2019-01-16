import tkinter as tk
from tkinter import ttk
from pathlib import Path

from ui.textarea import TextArea
from ui.linegutter import LineGutter

SRC_PATH = Path(__file__).parent.parent
RESOURCES_PATH = SRC_PATH.joinpath("./resources/")
print(RESOURCES_PATH)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        window_icon_path = RESOURCES_PATH.joinpath("icon.png").resolve()
        print(window_icon_path)
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

        # TODO : re-implement the ttk style for scrollbar to give us more control
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

        # menu bar
        self.menu_bar = self.create_menu_bar()
        self.configure(menu=self.menu_bar)

        # context menu
        self.context_menu = self.create_context_menu()

        # do element packing
        # status_bar **must** come before text_area to pack correctly
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.line_gutter.pack(side=tk.LEFT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.status_bar_text.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

        # set up event handling
        self.bind_events()

        # set focus to the text area and update line/column
        self.text_area.focus_set()
        self.update_index()

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

        # context menu event
        self.text_area.bind("<Button-3>", self.show_context_menu)

        # handle special text area events
        self.text_area.bind("<BackSpace>", self.on_key_backspace)

    def on_key_backspace(self, event=None):
        line, col = self.get_current_line_column()

        if col == "0" and line != "1":
            start, end = f"{int(line) - 1}.{tk.END}", f"{line}.0"

            # deleting the line will also delete the last character in the above line. We'll need to replace it.
            char = self.text_area.get(f'{int(line)-1}.{tk.END}-1c', end).replace("\n", "")

            # basically double the regular character that will be accidentally removed so that it will stay there
            self.text_area.insert(start, char)
            self.text_area.delete(start, end)  # remove the newline character that defines the next line
            self.line_gutter.delete_line_num()
            return "break"

    def show_context_menu(self, event):
        x = self.winfo_x() + self.text_area.winfo_x() + event.x
        y = self.winfo_y() + self.text_area.winfo_y() + event.y
        self.context_menu.post(x, y)

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

    def get_current_line_column(self):
        cursor_position = self.text_area.index(tk.INSERT)
        line, col = str(cursor_position).split(".")
        return line, col

    def update_index(self, event=None):
        line, col = self.get_current_line_column()
        self.current_index.set(f"Ln {line}, Col {int(col) + 1}")

    def create_menu_bar(self):
        # without re-implementing the Menu object, properties like `background` are managed by the
        # Window Manager and can not be changed.
        menu = tk.Menu(self, tearoff=False)

        # Create "File" option
        file_menu = tk.Menu(self, tearoff=False)  # "tearoff" allows the menu to pop-out of the main window
        file_menu.add_command(label="New Window")
        file_menu.add_command(label="New File")
        file_menu.add_command(label="Open File...")
        file_menu.add_command(label="Open Folder...")
        file_menu.add_separator()
        file_menu.add_command(label="Settings")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")
        file_menu.add_command(label="Close All Tabs")

        # Create "Edit" option
        edit_menu = tk.Menu(self, tearoff=False)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        edit_menu.add_command(label="Select All")

        # Add menus to main menu bar
        menu.add_cascade(label="File", menu=file_menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        return menu

    def create_context_menu(self):
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(label="Undo")
        menu.add_command(label="Redo")
        menu.add_separator()
        menu.add_command(label="Cut")
        menu.add_command(label="Copy")
        menu.add_command(label="Paste")
        menu.add_command(label="Select All")
        return menu


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
