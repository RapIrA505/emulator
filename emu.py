import shlex
import os

vfs_name = os.getlogin()
exit_cmd = "exit"


def do_ls(args):
    """Реализация команды ls с поддержкой путей"""
    target_dir = '.' if not args else args[0]

    try:
        entries = os.listdir(target_dir)
        for entry in entries:
            print(entry)
    except FileNotFoundError:
        print(f"ls: cannot access '{target_dir}': No such file or directory")
    except PermissionError:
        print(f"ls: cannot open directory '{target_dir}': Permission denied")


def do_cd(args):
    """Реализация команды cd с обработкой ошибок"""
    if not args:
        new_dir = os.path.expanduser("~")
    else:
        new_dir = args[0]

    try:
        os.chdir(new_dir)
    except FileNotFoundError:
        print(f"cd: no such file or directory: {new_dir}")
    except PermissionError:
        print(f"cd: permission denied: {new_dir}")
    except NotADirectoryError:
        print(f"cd: not a directory: {new_dir}")

def do_pwd(args):
    """Реализация команды pwd - вывод текущей рабочей директории"""
    print(os.getcwd())

def main():
    while True:
        try:
            command = input(vfs_name + " ")
            parts = shlex.split(command)
        except KeyboardInterrupt:
            print()
            break

        if not parts:
            continue

        cmd = parts[0]
        args = parts[1:]

        if cmd == exit_cmd:
            break
        elif cmd == 'ls':
            do_ls(args)
        elif cmd == 'cd':
            do_cd(args)
        elif cmd == 'pwd':
            do_pwd(args)
        else:
            print(f'{cmd}: command not found')


if __name__ == "__main__":
    main()