import contextlib
import sys
import threading
import time

import customtkinter as ctk
import pynput.keyboard as keyboard
import pynput.mouse as mouse
from exceptions import AbortedException

from modules.copy_from_excel import CopyFromExcel
from modules.copy_with_step import CopyWithStep
from views.input_view import InputView
from views.output_log_frame import OutputLogFrame

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("dark-blue")  # Themes: blue (default), , green

copy_with_step = CopyWithStep()
copy_from_excel = CopyFromExcel()


class MyApp:
    WIDTH = 680
    HEIGHT = 480

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Copy Object")

        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.update()

        # self.root.minsize(self.root.winfo_width(), self.root.winfo_height())

        self.user_click_ready = threading.Event()
        self.cancelled = threading.Event()

        self.is_excel = ctk.BooleanVar(value=False)
        self.has_step = ctk.BooleanVar(value=False)
        self.skip_F2 = ctk.BooleanVar(value=False)
        self.file_path = ctk.StringVar()

        self.process_thread = None
        self.coordinates = None

        # Frames
        self.top_frame = ctk.CTkFrame(master=self.root, corner_radius=0)
        self.checkbox_frame = ctk.CTkFrame(self.top_frame)
        self.log_frame = OutputLogFrame(master=self.root)
        self.input_frame = InputView(app=self)

        # Buttons
        self.start_button = ctk.CTkButton(
            self.top_frame, text="Старт", command=self.start_process
        )

        # Checkboxes
        self.excel_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Excel",
            variable=self.is_excel,
            command=self.open_file_dialog,
        )

        self.step_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Шаг",
            variable=self.has_step,
        )

        self.f2_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Отключить F2",
            variable=self.skip_F2,
        )

        self.layout_widgets()
        self.start_keyboard_listener()

        self.root.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def layout_widgets(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)

        self.top_frame.grid_columnconfigure(1, weight=2)
        self.top_frame.grid_rowconfigure(1, weight=2)
        self.top_frame.grid(row=0, column=0, sticky=ctk.NSEW)

        self.log_frame.grid(row=1, column=0, padx=5, pady=5, sticky=ctk.NSEW)
        self.checkbox_frame.grid(row=1, columnspan=2, pady=10)
        self.input_frame.grid(row=2, column=0, padx=5, pady=5, sticky=ctk.NSEW)

        self.excel_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky=ctk.W)
        self.step_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky=ctk.W)
        self.f2_checkbox.grid(row=1, column=2, padx=10, pady=5, sticky=ctk.W)

        self.start_button.grid(row=1, column=2, padx=10, pady=5)

    def start_process(self):
        self.cancelled.clear()

        if self.process_thread is None or not self.process_thread.is_alive():
            self.start_button.configure(state=ctk.DISABLED)
            self.log_frame.update_log("Запуск копирования")

            self.input_frame.user_input_ready.clear()

            if not self.is_excel.get():
                self.process_thread = threading.Thread(
                    target=self.run_copy_with_step, daemon=True
                )
            else:
                self.process_thread = threading.Thread(
                    target=self.run_copy_from_excel, daemon=True
                )

            self.process_thread.start()
        else:
            self.log_frame.update_log("Процесс уже запущен.")

    def run_copy_with_step(self):
        try:
            first_coord = self.get_click_coordinates(
                "Сделайте клик на первом объекте первого списка (откуда копировать)"
            )

            second_coord = self.get_click_coordinates(
                "Сделайте клик на первом объекте второго списка (куда вставка)"
            )

            self.root.focus()

            iterations = self.get_int_input("Введите количество повторений")

            if self.has_step.get():
                first_step = self.get_int_input("Введите шаг первому экрану")
                second_step = self.get_int_input("Введите шаг второму экрану")
            else:
                first_step = 1
                second_step = 1

            self.log_frame.update_log(
                "Переключитесь на оба окна и подготовьтесь к копированию"
            )

            self.sleep(3)

            copy_with_step.execute(
                iterations,
                [first_coord, second_coord],
                first_step=first_step,
                second_step=second_step,
                skip_f2=self.skip_F2.get(),
                cancelled=self.cancelled,
            )

            self.log_frame.update_log("Процесс копирования завершен")
        except AbortedException as e:
            self.log_frame.update_log(e)
        finally:
            self.start_button.configure(state=ctk.NORMAL)

    def run_copy_from_excel(self):
        try:
            coord = self.get_click_coordinates("Сделайте клик на первый объект списка.")

            copy_from_excel.setup(self.skip_F2.get(), self.cancelled)
            copy_from_excel.load_workbook(self.file_path.get())

            self.log_frame.update_log(
                "Введите номер листа с которого осуществить копирование"
            )
            self.log_frame.update_log("Доступные листы:")
            for item in copy_from_excel.get_sheets():
                self.log_frame.update_log(item)

            sheet_index = (
                self.get_int_input("Введите номер листа в Excel для чтения") - 1
            )

            if not copy_from_excel.check_index(sheet_index):
                self.log_frame.update_log("Неверный номер листа.")
                return

            column_letter = self.get_str_input(
                "Введите букву столбца для чтения"
            ).upper()

            size = self.get_int_input(
                "Введите количество строк, которые требуется скопировать"
            )

            cell_values = copy_from_excel.read_excel_column(
                sheet_index, column_letter, size
            )

            copy_from_excel.close_workbook()

            self.log_frame.update_log(
                "Откройте окно для вставки и сделайте его активным"
            )
            self.sleep(3)

            copy_from_excel.paste_values(coord, cell_values)

            self.log_frame.update_log("Процесс копирования завершен")
        except AbortedException as e:
            self.log_frame.update_log(e)
        finally:
            self.start_button.configure(state=ctk.NORMAL)

    def sleep(self, delay: int = 3):
        time.sleep(3)
        for i in range(delay):
            if self.cancelled.is_set():
                raise AbortedException()

            self.log_frame.update_log(delay - i)
            time.sleep(1)

    def get_click_coordinates(self, message: str):
        self.start_click_linstener()
        self.log_frame.update_log(message)
        self.user_click_ready.wait()
        self.user_click_ready.clear()
        self.stop_click_linstener()
        return self.coordinates

    def get_int_input(self, message: str):
        while True:
            if self.cancelled.is_set():
                raise AbortedException()
            try:
                self.log_frame.update_log(message)
                self.input_frame.user_input_ready.wait()
                input_value = self.input_frame.user_input

                if input_value is None:
                    raise ValueError

                repetitions = int(input_value)
                return repetitions
            except ValueError:
                self.log_frame.update_log("Ошибка! Введите корректное число.")
            finally:
                self.input_frame.user_input_ready.clear()

    def get_str_input(self, message: str):
        def is_empty_or_whitespace(s):
            return s.strip() == ""

        while True:
            if self.cancelled.is_set():
                raise AbortedException()
            try:
                self.log_frame.update_log(message)
                self.input_frame.user_input_ready.wait()
                input_value = self.input_frame.user_input

                if input_value is None or is_empty_or_whitespace(input_value):
                    raise ValueError

                return input_value
            except ValueError:
                self.log_frame.update_log("Ошибка! Введите не пустое значение")
            finally:
                self.input_frame.user_input_ready.clear()

    def open_file_dialog(self):
        if not self.is_excel.get():
            return

        self.log_frame.update_log("Выбор файла Excel")
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Excel", ".xlsx")], defaultextension=".xlsx"
        )
        if file_path:
            self.log_frame.update_log(f"Выбран файл: {file_path}")
            self.file_path.set(file_path)
        else:
            self.log_frame.update_log("Файл не выбран")
            self.is_excel.set(False)

    def start_click_linstener(self):
        self.mouse_listener = mouse.Listener(on_click=self.on_global_click)
        self.mouse_listener.start()

    def stop_click_linstener(self):
        with contextlib.suppress(AttributeError):
            self.mouse_listener.stop()

    def on_global_click(self, x, y, button, pressed):
        if not pressed:
            return

        self.coordinates = (x, y)
        self.log_frame.update_log(f"Получены координаты: {x}, {y}")
        self.user_click_ready.set()

    def start_keyboard_listener(self):
        self.listener = keyboard.Listener(on_press=self.__on_press)
        self.listener.start()

    def stop_keyboard_listener(self):
        with contextlib.suppress(AttributeError):
            self.listener.stop()

    def __on_press(self, key):
        if (
            key in [keyboard.Key.esc]
            and self.process_thread
            and self.process_thread.is_alive()
        ):
            self.log_frame.update_log("Отмена операции")
            self.cancelled.set()

    def __on_closing(self, event=0):
        self.stop_keyboard_listener()
        self.root.destroy()
        sys.exit(0)


def main():
    root = ctk.CTk()
    app = MyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
