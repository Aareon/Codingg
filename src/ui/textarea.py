import tkinter as tk


class TextArea(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.config(wrap=tk.NONE)

        self._orig = f"{self._w}_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self.event_proxy)

    def event_proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig, *args)
        result = None

        # if we just ignore the exception, everything works out fine apparently
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
