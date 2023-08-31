from threading import Event
import time

import pyautogui

from exceptions import AbortedException


class CopyWithStep:
    def __init__(self):
        self.first_coord = None
        self.second_coord = None
        self.first_step = 1
        self.second_step = 1

    def perform_actions1(self, i):
        pyautogui.moveTo(self.first_coord)
        pyautogui.click()
        pyautogui.press("down", presses=i * self.first_step)
        if self.skip_f2 is False:
            pyautogui.press("f2")
        pyautogui.hotkey("ctrl", "c")
        pyautogui.hotkey("alt", "tab")

    def perform_actions2(self, i):
        pyautogui.moveTo(self.second_coord)
        pyautogui.click()
        pyautogui.press("down", presses=i * self.second_step)
        if self.skip_f2 is False:
            pyautogui.press("f2")
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
        pyautogui.hotkey("alt", "tab")

    def execute(
        self,
        iterations: int,
        coordinates,
        first_step: int = 1,
        second_step: int = 1,
        skip_f2: bool = True,
        cancelled: Event = Event(),
    ):
        self.first_coord = coordinates[0]
        self.second_coord = coordinates[1]
        self.first_step = first_step
        self.second_step = second_step
        self.skip_f2 = skip_f2

        for i in range(iterations):
            if cancelled.is_set():
                raise AbortedException()

            self.perform_actions1(i)
            time.sleep(0.1)
            self.perform_actions2(i)
