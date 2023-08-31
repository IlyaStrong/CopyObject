import tkinter
import customtkinter as ctk

from views.fonts.fonts import log_font, subheading_font


class OutputLogFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # configure grid layout (1x1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)  # log row will resize
        self.columnconfigure(0, weight=1)

        # Frame title
        self.lbl_title = ctk.CTkLabel(
            master=self,
            text="Лог",
            font=subheading_font(),
            justify=tkinter.LEFT,
        )
        self.lbl_title.grid(row=0, column=0, sticky="wns", padx=15, pady=15)

        # Text Box
        self.txt_log = tkinter.Text(
            master=self,
            wrap=tkinter.WORD,
            font=log_font(),
            bg="#343638",
            fg="#ffffff",
            padx=5,
            pady=5,
            spacing1=2,  # spacing before a line
            spacing3=2,  # spacing after a line / wrapped line
            cursor="arrow",
        )
        self.txt_log.grid(row=1, column=0, padx=(15, 0), pady=(0, 15), sticky=ctk.NSEW)
        self.txt_log.configure(state=tkinter.DISABLED)

        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(master=self, command=self.txt_log.yview)
        self.scrollbar.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky=ctk.NS)

        # Connect textbox scroll event to scrollbar
        self.txt_log.configure(yscrollcommand=self.scrollbar.set)

    def update_log(self, msg, overwrite=False):
        """
        Called from controller. Updates the log with given message. If overwrite is True,
        the last line will be cleared before the message is added.
        """
        self.txt_log.configure(state=tkinter.NORMAL)
        if overwrite:
            self.txt_log.delete("end-1c linestart", "end")

        self.txt_log.insert(tkinter.END, f"{msg}\n")
        self.txt_log.configure(state=tkinter.DISABLED)
        self.txt_log.see(tkinter.END)

    def clear_log(self):
        """
        Called from controller. Clears the log.
        """
        self.txt_log.configure(state=tkinter.NORMAL)
        self.txt_log.delete(1.0, tkinter.END)
        self.txt_log.configure(state=tkinter.DISABLED)
        self.txt_log.see(tkinter.END)
