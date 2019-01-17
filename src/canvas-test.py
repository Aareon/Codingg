import tkinter as tk


class LineGutter(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_area = None

    def attach(self, text_area):
        self.text_area = text_area

    def redraw(self):
        """redraw line numbers"""
        self.delete("all")

        i = self.text_area.index("@0,0")
        while True:
            dline = self.text_area.dlineinfo(i)
            if dline is None:
                break

            y = dline[1]
            line_num = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=line_num)
            i = self.text_area.index(f"{i}+1line")


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config(wrap="none")

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self.event_proxy)

    def event_proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = None

        try:
            result = self.tk.call(cmd)
        except tk.TclError as exc:
            if str(exc) == "text doesn't contain any characters tagged with \"sel\"":
                pass

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (
            args[0] in ("insert", "replace", "delete")
            or args[0:3] == ("mark", "set", "insert")
            or args[0:2] == ("xview", "moveto")
            or args[0:2] == ("xview", "scroll")
            or args[0:2] == ("yview", "moveto")
            or args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result


class Example(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_area = CustomText(self)
        self.vsb = tk.Scrollbar(orient="vertical", command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.vsb.set)
        self.text_area.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
        self.line_gutter = LineGutter(self, width=30)
        self.line_gutter.attach(self.text_area)

        self.vsb.pack(side="right", fill="y")
        self.line_gutter.pack(side="left", fill="y")
        self.text_area.pack(side="right", fill="both", expand=True)

        self.text_area.bind("<<Change>>", self._on_change)
        self.text_area.bind("<Configure>", self._on_change)

    def _on_change(self, event=None):
        self.line_gutter.redraw()


if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
