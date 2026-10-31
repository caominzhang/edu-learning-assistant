"""Windows entry: settings and service lifecycle, using the same app as NAS."""
import json
import os
import socket
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import webbrowser

DATA = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'EDULearningAssistant'
DATA.mkdir(parents=True, exist_ok=True)
CONFIG = DATA / 'settings.json'

def main():
    root = tk.Tk()
    root.title('EDU 学习助手 0.2.0-preview.1')
    root.geometry('480x280')
    tk.Label(root, text='家庭学习档案 · Windows 独立版', font=('', 16)).pack(pady=14)
    tk.Label(root, text='孩子姓名（可用昵称，供图片姓名匹配使用）').pack()
    name = tk.StringVar()
    try:
        name.set(json.loads(CONFIG.read_text(encoding='utf-8')).get('student', ''))
    except (OSError, ValueError):
        pass
    entry = tk.Entry(root, textvariable=name, width=30)
    entry.pack(pady=8)
    status = tk.StringVar(value='启动后在浏览器使用；关闭此窗口会停止服务。')
    tk.Label(root, textvariable=status, wraplength=450).pack(pady=10)
    server = None
    address = None

    def start():
        nonlocal server, address
        if server:
            webbrowser.open(address)
            return
        student = name.get().strip()
        if not student or len(student) > 40:
            messagebox.showerror('请检查姓名', '请输入1至40字的姓名或昵称。')
            return
        try:
            CONFIG.write_text(json.dumps({'student': student}, ensure_ascii=False, indent=2), encoding='utf-8')
            os.environ.update(TRACKER_DATA=str(DATA), TRACKER_STUDENT=student,
                              TRACKER_HOST='127.0.0.1', TRACKER_PORT='0', TRACKER_PASSWORD='')
            import app
            server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
            address = f'http://127.0.0.1:{server.server_address[1]}'
            threading.Thread(target=server.serve_forever, daemon=True).start()
            entry.config(state='disabled')
            status.set('正在运行：' + address + '\n关闭此窗口会停止服务。')
            webbrowser.open(address)
        except Exception as exc:
            messagebox.showerror('启动失败', str(exc))

    def close():
        if server:
            server.shutdown()
            server.server_close()
        root.destroy()

    tk.Button(root, text='启动 / 打开学习档案', command=start, width=26).pack(pady=5)
    tk.Button(root, text='打开数据目录', command=lambda: os.startfile(DATA)).pack(pady=5)
    root.protocol('WM_DELETE_WINDOW', close)
    root.mainloop()

if __name__ == '__main__':
    main()
