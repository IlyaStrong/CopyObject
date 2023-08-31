from pynput.mouse import Listener
import keyboard
import threading
import time
import pyautogui
import sys
stop=False

def exit_on_esc():
    """
    Непрерывно проверяет нажатые клавиши
    В случае нажатия ESC переменная выхода меняется на True и происходит выход
    :return:
    """

    while True:
        key=keyboard.read_key()
        if key in ['esc']:
            global stop
            stop=True
            sys.exit()

def get_click_coordinates(message):
    print(message)
    coord1 = None
    coord2 = None
    click_count = 0

    def on_click(x, y, button, pressed):
        nonlocal coord1, coord2, click_count
        if pressed:
            click_count += 1
            if click_count == 1:
                coord1 = (x, y)
                print("Сделайте клик на первом объекте второго списка (куда будет вставка)")
            elif click_count == 2:
                coord2 = (x, y)
                return False  # Останавливаем слушателя после получения двух координат

    with Listener(on_click=on_click) as listener:
        listener.join()

    return coord1, coord2

def get_repetitions():
    while True:
        try:
            if stop==True:
                sys.exit()
            repetitions = int(input("Введите количество повторений и нажмите Enter: "))
            return repetitions
        except ValueError:
            print("Ошибка! Введите корректное число.")

def get_step():
    while True:
        try:
            step1 = int(input("Введите шаг первому экрану и нажмите Enter: "))
            step2 = int(input("Введите шаг второму экрану и нажмите Enter: "))
            return step1, step2
        except ValueError:
            print("Ошибка! Введите корректное число.")


def perform_actions1(coord1, i, step1):
    pyautogui.moveTo(coord1)
    pyautogui.click()
    pyautogui.press('down', presses=i*step1)
    pyautogui.press('f2')
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.hotkey('alt', 'tab')

def perform_actions2(coord2, i, step2):
    pyautogui.moveTo(coord2)
    pyautogui.click()
    pyautogui.press('down', presses=i*step2)
    pyautogui.press('f2')
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')
    pyautogui.hotkey('alt', 'tab')            

def main():

    coord1, coord2 = get_click_coordinates("Сделайте клик на первом объекте первого списка (откуда будем копировать)")
    repetitions = get_repetitions()
    step1, step2 = get_step()

    print('Переключитесь на оба окна и подготовьтесь к копированию')
    time.sleep(3)
    for i in range(3):
        print(3-i)
        time.sleep(1)

    for i in range(repetitions):
        if stop == True:
            sys.exit()
        perform_actions1(coord1, i, step1)
        perform_actions2(coord2, i, step2)    

if __name__ == "__main__":
    exit_thread = threading.Thread(target=exit_on_esc)
    exit_thread.start()
    main_thread = threading.Thread(target=main)
    main_thread.start()
