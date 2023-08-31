from threading import Event
import customtkinter as ctk


class InputView(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app.root, **kwargs)

        self.app = app

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)  # log row will resize
        self.columnconfigure(0, weight=2)

        self.input_textbox = ctk.CTkEntry(self, placeholder_text="Поле для ввода")
        self.send_button = ctk.CTkButton(self, text="Ввод", command=self.send_input)

        self.input_textbox.bind('<Return>', self.send_input)


        self.input_value = None
        self.user_input = None
        self.user_input_ready = Event()

        self.__layout_widgets()

    def __layout_widgets(self):
        self.input_textbox.grid(row=0, column=0, padx=10, pady=10, sticky=ctk.NSEW)
        self.send_button.grid(row=0, column=1, padx=10, pady=10)

    def send_input(self, event = None):
        self.user_input = self.input_textbox.get()
        self.user_input_ready.set()
        self.app.log_frame.update_log(f"{self.user_input}")
        self.input_textbox.delete(0, ctk.END)
