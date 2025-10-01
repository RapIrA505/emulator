import shlex
import os
import tkinter as tk
from tkinter import scrolledtext

vfs_name = os.getlogin()
exit_cmd = "exit"

def do_parc(args, output_func):
    if os.getenv(args) is not None:
        output_func(os.getenv(args))

def do_ls(args, output_func):
    """Реализация команды ls с поддержкой путей"""
    target_dir = '.' if not args else args[0]

    try:
        entries = os.listdir(target_dir)
        for entry in entries:
            output_func(entry)
    except FileNotFoundError:
        output_func(f"ls: cannot access '{target_dir}': No such file or directory")
    except PermissionError:
        output_func(f"ls: cannot open directory '{target_dir}': Permission denied")


def do_cd(args, output_func):
    """Реализация команды cd с обработкой ошибок"""
    if not args:
        new_dir = os.path.expanduser("~")
    else:
        new_dir = args[0]

    try:
        os.chdir(new_dir)
    except FileNotFoundError:
        output_func(f"cd: no such file or directory: {new_dir}")
    except PermissionError:
        output_func(f"cd: permission denied: {new_dir}")
    except NotADirectoryError:
        output_func(f"cd: not a directory: {new_dir}")


def do_pwd(args, output_func):
    """Реализация команды pwd - вывод текущей рабочей директории"""
    output_func(os.getcwd())


def execute_command(command, output_widget):
    """Выполняет команду и выводит результат в виджет"""
    # Добавляем команду в вывод
    output_widget.config(state=tk.NORMAL)
    output_widget.insert(tk.END, f"{vfs_name} {command}\n")

    parts = shlex.split(command)
    if not parts:
        output_widget.config(state=tk.DISABLED)
        output_widget.see(tk.END)
        return

    cmd = parts[0]
    args = parts[1:]

    # Функция для вывода в текстовый виджет
    def output_func(text):
        output_widget.insert(tk.END, f"{text}\n")

    if cmd == exit_cmd:
        output_widget.config(state=tk.DISABLED)
        output_widget.see(tk.END)
        return "exit"
    elif cmd == 'ls':
        do_ls(args, output_func)
    elif cmd == 'cd':
        do_cd(args, output_func)
    elif cmd == 'pwd':
        do_pwd(args, output_func)
    elif cmd[0] == '$':
        do_parc(cmd[1:], output_func)
    else:
        output_func(f'{cmd}: command not found')

    # Блокируем текстовое поле и прокручиваем к концу
    output_widget.config(state=tk.DISABLED)
    output_widget.see(tk.END)


def main():
    # Создаем главное окно
    root = tk.Tk()
    root.title("Terminal")
    root.configure(bg='black')

    # Создаем текстовое поле для вывода (только для чтения)
    output_text = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        bg='black',
        fg='white',
        insertbackground='white',
        font=('Courier', 10),
        height=25,
        width=80,
        state=tk.DISABLED  # Блокируем редактирование
    )
    output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    # Создаем поле для ввода команды
    input_frame = tk.Frame(root, bg='black')
    input_frame.pack(fill=tk.X, padx=5, pady=5)

    prompt_label = tk.Label(
        input_frame,
        text=f"{vfs_name} ",
        bg='black',
        fg='white',
        font=('Courier', 10)
    )
    prompt_label.pack(side=tk.LEFT)

    command_entry = tk.Entry(
        input_frame,
        bg='black',
        fg='white',
        insertbackground='white',
        font=('Courier', 10),
        width=70
    )
    command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    command_entry.focus()

    def on_enter(event):
        command = command_entry.get()
        command_entry.delete(0, tk.END)

        result = execute_command(command, output_text)
        if result == "exit":
            root.quit()

    command_entry.bind('<Return>', on_enter)

    # Обработчик закрытия окна
    def on_closing():
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Запускаем главный цикл
    root.mainloop()


if __name__ == "__main__":
    main()