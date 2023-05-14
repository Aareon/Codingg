import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from ui.linegutter import LineGutter
from ui.textarea import TextArea
from ui.filetab import FileTab
from ui.notebook import CustomNotebook

SRC_PATH = Path(__file__).parent.resolve()
RESOURCES_PATH = SRC_PATH.joinpath("../resources/").resolve()

DEFAULT_EDITOR_CONFIG = {
    "font": ("Consolas", 12),
    "tabsize": 4,
    "tab-to-spaces": True,
    "show-welcome": True,
}

WELCOME_MESSAGE = """Welcome to Codingg!
This is a simple text editor written in Python using Tkinter."""


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.lift()

        # set window icon
        window_icon_path = RESOURCES_PATH.joinpath("favicon.png").resolve()
        self.call("wm", "iconphoto", self._w, tk.Image("photo", file=window_icon_path))

        self.title("untitled — Codingg")

        self.background = "#282c34"

        # load config
        self.editor_config = DEFAULT_EDITOR_CONFIG

        # The `highlightthickness` option used below ensures that a border won't
        # be added to the sides of each widget when the window loses focus.
        # This behavior was only noticed on Linux machines (Arch/Ubuntu 18.04).

        # status bar
        self.current_index = tk.StringVar()
        self.status_bar = tk.Text(
            self, bg="#21252b", fg="#9da5b4", borderwidth=0, highlightthickness=0
        )
        self.status_bar_text = tk.Label(
            self.status_bar,
            bg=self.status_bar["bg"],
            fg=self.status_bar["fg"],
            textvar=self.current_index,
        )

        # menu bar
        self.menu_bar = self.create_menu_bar()
        self.configure(menu=self.menu_bar)

        self.open_tabs = []
        self.viewing_tab = None

        # create notebook for tabs
        self.notebook = CustomNotebook(self, style="TNotebook")
        self.notebook.enable_traversal()

        # TODO : re-implement the ttk style for scrollbar to give us more control

        # context menu
        self.context_menu = self.create_context_menu()

        # do element packing
        # status_bar **must** come before text_area to pack correctly
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar_text.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

        if self.editor_config["show-welcome"]:
            self.open_welcome_tab()

        # set up event handling
        self.bind_events()

    def bind_new_tab_events(self, tab):
        # status bar events
        tab.text_area.bind("<KeyRelease>", self.update_index)  # update line and column
        tab.text_area.bind("<ButtonRelease-1>", self.update_index)

        # context menu event
        tab.text_area.bind("<Button-3>", self.show_context_menu)

        # handle tab key
        tab.text_area.bind("<Tab>", self.insert_spaces)

    def open_new_tab(self, fp: Path = None, text: str = None, title: str = "untitled"):
        tab = FileTab(self.notebook)
        title = fp.name if fp else title
        tab.scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.scroll_text)
        tab.text_area = TextArea(
            tab,
            bg="#282c34",
            fg="#abb2bf",
            insertbackground="#528bff",
            borderwidth=0,
            highlightthickness=0,  # disable highlighting this
            undo=True,
        )

        tab.line_gutter = LineGutter(
            tab,
            tab.text_area,
            bg="#282c34",
            fg="#4b5364",  # `fg` refers to the text widget within the LineGutter Canvas
            borderwidth=0,
            highlightthickness=0,
            width=30,
        )
        self.notebook.add(tab, text=title)

        self.bind_new_tab_events(tab)

        self.open_tabs.append(tab)

        tab.text_area.insert("1.0", text or fp.read_text(encoding="utf-8"))

        # set focus to the text_area area and update line/column
        self.notebook.select(len(self.open_tabs) - 1)
        tab.text_area.focus_set()
        self.update_index()
        self.viewing_tab = tab

    def open_welcome_tab(self):
        self.open_new_tab(title="Welcome to Codingg", text=WELCOME_MESSAGE)

    @property
    def current_tab(self):
        return self.open_tabs[self.notebook.index("current")]

    def handle_tab_changed(self, event):
        self.viewing_tab.scrollbar.pack_forget()
        self.viewing_tab.text_area.pack_forget()
        self.viewing_tab.line_gutter.pack_forget()

        self.viewing_tab = self.current_tab
        self.viewing_tab.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.pack(fill=tk.BOTH, expand=1)
        self.viewing_tab.line_gutter.pack(side=tk.LEFT, fill=tk.Y)
        self.viewing_tab.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def bind_events(self):
        # handle F11 key
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Control_L>n", lambda e: self.open_new_tab(text="Open new file or select a language.\nStart typing and save to create an new file."))
        self.notebook.bind("<<NotebookTabChanged>>", self.handle_tab_changed)

    def insert_spaces(self, event):
        current_tab = self.current_tab
        if self.editor_config.get(
            "tab-to-spaces", DEFAULT_EDITOR_CONFIG["tab-to-spaces"]
        ):
            current_tab.text_area.insert(
                tk.INSERT,
                " " * self.editor_config("tabsize", DEFAULT_EDITOR_CONFIG["tabsize"]),
            )
            return "break"
        else:
            current_tab.text_area.insert(tk.INSERT, "\t")
            return "break"

    def show_context_menu(self, event):
        current_tab = self.current_tab
        x = self.winfo_x() + current_tab.text_area.winfo_x() + event.x
        y = self.winfo_y() + current_tab.text_area.winfo_y() + event.y
        current_tab.context_menu.post(x, y)

    def scroll_text(self, *args):
        if len(args) > 1:
            self.current_tab.text_area.yview_moveto(args[1])
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

    def get_current_line_column(self):
        cursor_position = self.current_tab.text_area.index(tk.INSERT)
        line, col = str(cursor_position).split(".")
        return line, col

    def update_index(self, event=None):
        line, col = self.get_current_line_column()
        self.current_index.set(f"Ln {line}, Col {int(col) + 1}")

    def open_file(self):
        fp = filedialog.askopenfilename(
            filetypes=(
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("Python files", "*.py*"),
                ("Javascript files", "*.js"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("Markdown files", "*.md"),
                ("PHP files", "*.php"),
                ("Java files", "*.java"),
                ("C files", "*.c"),
                ("C++ files", "*.cpp"),
                ("C# files", "*.cs"),
                ("Go files", "*.go"),
                ("Ruby files", "*.rb"),
                ("Rust files", "*.rs"),
                ("Swift files", "*.swift"),
                ("Lua files", "*.lua"),
                ("YAML files", "*.yaml"),
                ("JSON files", "*.json"),
                ("TOML files", "*.toml"),
                ("INI files", "*.ini"),
            )
        )
        self.open_new_tab(fp=Path(fp))

    def create_menu_bar(self):
        # without re-implementing the Menu object
        # properties like `background` are managed by the
        # Window Manager and can not be changed.
        menu = tk.Menu(self, tearoff=False)

        # Create "File" option
        file_menu = tk.Menu(
            self, tearoff=False
        )  # "tearoff" allows the menu to pop-out of the main window
        file_menu.add_command(label="New Window")
        file_menu.add_command(label="New File")
        file_menu.add_command(label="Open File...", command=self.open_file)
        file_menu.add_command(label="Open Folder...")
        file_menu.add_separator()
        file_menu.add_command(label="Settings")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")
        file_menu.add_command(label="Close All Tabs")

        # Create "Edit" option
        edit_menu = tk.Menu(self, tearoff=False)
        edit_menu.add_command(
            label="Undo",
            command=lambda: self.current_tab.text_area.event_generate("<<Undo>>"),
        )
        edit_menu.add_command(
            label="Redo",
            command=lambda: self.current_tab.text_area.event_generate("<<Redo>>"),
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Cut",
            command=lambda: self.current_tab.text_area.event_generate("<<Cut>>"),
        )
        edit_menu.add_command(
            label="Copy",
            command=lambda: self.current_tab.text_area.event_generate("<<Copy>>"),
        )
        edit_menu.add_command(
            label="Paste",
            command=lambda: self.current_tab.text_area.event_generate("<<Paste>>"),
        )
        edit_menu.add_command(
            label="Select All",
            command=lambda: self.current_tab.text_area.event_generate("<<SelectAll>>"),
        )

        # Add menus to main menu bar
        menu.add_cascade(label="File", menu=file_menu)
        menu.add_cascade(label="Edit", menu=edit_menu)
        return menu

    def create_context_menu(self):
        menu = tk.Menu(self, tearoff=False)
        menu.add_command(
            label="Undo",
            command=lambda: self.current_tab.text_area.event_generate(
                "<<Undo>>"
            ),  # TOODO: get current tab FIX ME
        )
        menu.add_command(
            label="Redo",
            command=lambda: self.current_tab.text_area.event_generate("<<Redo>>"),
        )
        menu.add_separator()
        menu.add_command(
            label="Cut",
            command=lambda: self.current_tab.text_area.event_generate("<<Cut>>"),
        )
        menu.add_command(
            label="Copy",
            command=lambda: self.current_tab.text_area.event_generate("<<Copy>>"),
        )
        menu.add_command(
            label="Paste",
            command=lambda: self.current_tab.text_area.event_generate("<<Paste>>"),
        )
        menu.add_command(
            label="Select All",
            command=lambda: self.current_tab.text_area.event_generate("<<SelectAll>>"),
        )
        return menu


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
