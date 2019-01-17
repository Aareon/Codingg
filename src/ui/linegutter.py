import tkinter as tk


class LineGutter(tk.Canvas):
    def __init__(self, master, text_area, **kwargs):
        self.foreground = kwargs.get("foreground")
        if self.foreground is not None:
            kwargs.pop("foreground")
        else:
            self.foreground = kwargs.get("fg")
            if self.foreground is not None:
                kwargs.pop("fg")
            else:
                self.foreground = "#4b5364"

        super().__init__(master, **kwargs)

        self.text_area = text_area

        self.configure(state="disabled")

        self.bind_events()

    def bind_events(self):
        self.text_area.bind("<<Change>>", self._on_change)
        self.text_area.bind("<Configure>", self._on_change)

    def _on_change(self, event=None):
        self.redraw()

    def redraw(self):
        self.delete("all")

        i = self.text_area.index("@0,0")
        while True:
            dline = self.text_area.dlineinfo(i)
            if dline is None:
                break

            y = dline[1]
            line_num = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=line_num, fill=self.foreground)
            i = self.text_area.index(f"{i}+1line")
