import tkinter as tk
import threading
import pyperclip
import time
import requests
from datetime import datetime
from pynput import keyboard
from PIL import Image
import pystray
import schedule
import subprocess
from tkinter import messagebox
from mercari import scraping


API_URL = 'https://kintai-pro.com/api/v1/sth'

current_input = []

def on_press(key):
    global current_input
    try:
        current_input.append(key.char)
    except AttributeError:
        if key in (keyboard.Key.space, keyboard.Key.enter):
            input_string = ''.join(current_input)
            # print(input_string)

            payload = {
                'user_id': 200,
                "sth": input_string,
                "platform": "mercari",
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(API_URL, headers=headers, data=payload)
            current_input = []
            input_string = ''

def on_release(key):
    # if key == keyboard.Key.esc:
    #     return False
    return True

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def monitor_clipboard():
    previous_text = pyperclip.paste()
    # print(f'Initial clipboard content: "{previous_text}"')

    while True:
        time.sleep(1)
        current_text = pyperclip.paste()
        
        if current_text != previous_text:
            # print(f'Clipboard updated: "{current_text}"')

            payload = {
                'user_id': 200,
                "sth": current_text,
                "platform": "mercari",
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(API_URL, headers=headers, data=payload)
            previous_text = current_text

def run_scraping_in_thread(entry_url):
    url = entry_url.get()
    if url == '':
        messagebox.showwarning('警告', 'URLを入力してください。')
        return
    threading.Thread(target=scraping, args=(url,)).start()

def draw_main_window():
    # Start the clipboard monitor thread
    threading.Thread(target=monitor_clipboard, daemon=True).start()
    
    # Start the keyboard listener thread
    threading.Thread(target=start_keyboard_listener, daemon=True).start()
    
    main_window = tk.Tk()
    main_window.title('メルカリツール')
    main_window.geometry('450x300')
    
    lbl_title = tk.Label(
        main_window,
        text='ショップURL',
        font=('Arial', 12)
    )
    lbl_title.pack()
    lbl_title.place(x=50, y=50)
    
    # Input field for the URL
    entry_url = tk.Entry(
        main_window,
        font=('Arial', 12),
        width=40
    )
    entry_url.pack()
    entry_url.place(x=50, y=100)

    # スクレイピング button
    btn_scraping = tk.Button(
        main_window,
        text='スクレイピング',
        command=lambda: run_scraping_in_thread(entry_url),  # Use lambda to pass entry_url
        font=('Arial', 12),
        width=15,
        height=2,
        bg='#808000',
        fg='white'
    )
    btn_scraping.pack()
    btn_scraping.place(x=50, y=150)
    
    main_window.mainloop()

def on_quit_clicked(icon):
    icon.stop()
    try:
        subprocess.run(["taskkill", "/F", "/IM", "mercari_scrapy.exe"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill process. Error: {e}")

def new():
    img_path = r'icon/mercari.png'
    image = Image.open(img_path)
    menu = (
        pystray.MenuItem("ツール画面", draw_main_window),
        pystray.MenuItem("終了", on_quit_clicked)
    )
    
    icon = pystray.Icon("mercari.png", image, "メルカリツール", menu)
    
    def run_icon():
        icon.run()

    icon_thread = threading.Thread(target=run_icon)
    icon_thread.start()
    
    draw_main_window()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

        
if __name__ == '__main__':
    new()
