import tkinter as tk
from tkinter import ttk
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path

RES_PATH = Path(__file__).parent.parent.parent / "resources"

CLOSE_ICON_SIZE = 20

image = Image.open(RES_PATH / "close.png").resize((CLOSE_ICON_SIZE, CLOSE_ICON_SIZE))
buffered = BytesIO()
image.save(buffered, format="PNG")
close_img = base64.b64encode(buffered.getvalue())

image = Image.open(RES_PATH / "close_focus.png").resize((CLOSE_ICON_SIZE, CLOSE_ICON_SIZE))
buffered = BytesIO()
image.save(buffered, format="PNG")
close_focus_img = base64.b64encode(buffered.getvalue())

image = Image.open(RES_PATH / "close_press.png").resize((CLOSE_ICON_SIZE, CLOSE_ICON_SIZE))
buffered = BytesIO()
image.save(buffered, format="PNG")
close_press_img = base64.b64encode(buffered.getvalue())


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, background="#282c34", **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        # Import the Notebook.tab element from the default theme
        self.styler = ttk.Style()
        try:
            self.styler.element_create("CustomNotebook.Tab", "from", "default")
        except tk.TclError:
            # CustomNotebook.tab already exists
            pass
        self.styler.configure("CustomNotebook.Tab", background=background)
        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(["pressed"])
            self._active = index
            return "break"

    def on_close_release(self, event):
        """Called when the button is released"""
        if not self.instate(["pressed"]):
            return

        element = self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage(
                "img_close",
                data=close_img,
            ),
            tk.PhotoImage(
                "img_closeactive",
                data=close_focus_img,
            ),
            tk.PhotoImage(
                "img_closepressed",
                data=close_press_img,
            ),
        )

        style.element_create(
            "close",
            "image",
            "img_close",
            ("active", "pressed", "!disabled", "img_closepressed"),
            ("active", "!disabled", "img_closeactive"),
            border=8,
            sticky="",
        )
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout(
            "CustomNotebook.Tab",
            [
                (
                    "CustomNotebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "CustomNotebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "CustomNotebook.focus",
                                            {
                                                "side": "top",
                                                "sticky": "nswe",
                                                "children": [
                                                    (
                                                        "CustomNotebook.label",
                                                        {"side": "left", "sticky": ""},
                                                    ),
                                                    (
                                                        "CustomNotebook.close",
                                                        {"side": "left", "sticky": ""},
                                                    ),
                                                ],
                                            },
                                        )
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        )


if __name__ == "__main__":
    root = tk.Tk()

    notebook = CustomNotebook(width=200, height=200)
    notebook.pack(side="top", fill="both", expand=True)

    for color in ("red", "orange", "green", "blue", "violet"):
        frame = tk.Frame(notebook, background=color)
        notebook.add(frame, text=color)

    root.mainloop()
