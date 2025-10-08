import shlex
import os
import tkinter as tk
from tkinter import scrolledtext
import argparse
import stat
import datetime

vfs_name = os.getlogin()
exit_cmd = "exit"

# Глобальные переменные для конфигурации
vfs_path = None
startup_script = None
script_dir = os.path.dirname(os.path.abspath(__file__))


# VFS структуры
class VFSNode:
    def __init__(self, name, is_directory=True, content=None, owner=None, group=None):
        self.name = name
        self.is_directory = is_directory
        self.content = content if content else ({} if is_directory else '')
        self.children = {} if is_directory else None
        self.parent = None
        self.owner = owner if owner else vfs_name  # По умолчанию - текущий пользователь
        self.group = group if group else "users"   # По умолчанию - группа users

    def get_path(self):
        path_parts = []
        current = self
        while current and current.name:
            path_parts.append(current.name)
            current = current.parent
        return '/' + '/'.join(reversed(path_parts))


class VFS:
    def __init__(self):
        self.root = VFSNode("", is_directory=True)
        self.current_dir = self.root
        self.loaded = False
        self.loaded_items_count = 0

    def load_from_directory(self, real_path):
        """Загрузка VFS - если путь None, создает образцовую структуру, иначе загружает из реальной директории"""
        if real_path is None:
            # Создаем образцовую структуру
            print("Создаем образцовую структуру VFS...")
            self._create_sample_structure()
            self.loaded = True
            return True
        else:
            # Загружаем из реальной директории
            return self.load_from_real_directory(real_path)

    def load_from_real_directory(self, real_path):
        """Загружает VFS из реальной директории"""
        if not real_path or not os.path.exists(real_path):
            return False

        if not os.path.isdir(real_path):
            return False

        print(f"Загружаем VFS из реальной директории: {real_path}")

        # Сбрасываем текущую VFS
        self.root = VFSNode("", is_directory=True)
        self.current_dir = self.root
        self.loaded_items_count = 0

        # Рекурсивно загружаем структуру
        try:
            self._load_directory_recursive(real_path, self.root)
            self.loaded = True
            return True
        except Exception as e:
            print(f"Ошибка загрузки VFS: {e}")
            return False

    def _load_directory_recursive(self, real_path, vfs_node):
        """Рекурсивно загружает директорию в VFS"""
        try:
            for item_name in os.listdir(real_path):
                # Пропускаем скрытые файлы, начинающиеся с .
                if item_name.startswith('.'):
                    continue

                real_item_path = os.path.join(real_path, item_name)

                if os.path.isdir(real_item_path):
                    # Создаем директорию в VFS
                    new_dir = VFSNode(item_name, is_directory=True)
                    new_dir.parent = vfs_node
                    vfs_node.children[item_name] = new_dir
                    vfs_node.content[item_name] = new_dir
                    self.loaded_items_count += 1

                    # Рекурсивно загружаем содержимое
                    self._load_directory_recursive(real_item_path, new_dir)
                else:
                    # Создаем файл в VFS
                    try:
                        # Читаем только текстовые файлы
                        if item_name.endswith(('.txt', '.py', '.md', '.html', '.css', '.js', '.json')):
                            with open(real_item_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        else:
                            content = f"Бинарный файл: {item_name}"
                    except:
                        content = f"Содержимое файла {item_name}"

                    new_file = VFSNode(item_name, is_directory=False, content=content)
                    new_file.parent = vfs_node
                    vfs_node.children[item_name] = new_file
                    vfs_node.content[item_name] = content
                    self.loaded_items_count += 1

        except PermissionError:
            print(f"Нет доступа к: {real_path}")

    def _create_sample_structure(self):
        """Создает образцовую структуру VFS"""
        self.root = VFSNode("", is_directory=True)
        self.current_dir = self.root

        # Создаем тестовую структуру с 3 уровнями вложенности
        # Уровень 1
        folders_l1 = ["documents/", "pictures/", "music/", "projects/"]
        files_l1 = {
            "readme.txt": "Добро пожаловать в VFS!\nЭто виртуальная файловая система.\n" +
                          "Эта строка 1\nЭта строка 2\nЭта строка 3\nЭта строка 4\nЭта строка 5\n" +
                          "Эта строка 6\nЭта строка 7\nЭта строка 8\nЭта строка 9\nЭта строка 10\n" +
                          "Эта строка 11\nЭта строка 12\nЭта строка 13\nЭта строка 14\nЭта строка 15",
            "hello.py": "print('Hello from VFS!')\n# This is a comment\nimport os\n\nprint('Goodbye')",
            "large_file.txt": "\n".join([f"Строка {i}" for i in range(1, 21)]),
            ".hidden_file": "Это скрытый файл",
        }

        # Уровень 2
        folders_l2 = {
            "documents": ["work/", "personal/"],
            "pictures": ["vacations/", "screenshots/"],
            "projects": ["python/", "web/"]
        }
        files_l2 = {
            "documents": ["report.pdf", "notes.txt"],
            "projects": ["todo.md", "ideas.txt"]
        }

        # Уровень 3
        files_l3 = {
            "documents/work": ["presentation.pptx", "budget.xlsx"],
            "documents/personal": ["diary.txt", "recipes.md"],
            "projects/python": ["main.py", "utils.py"],
            "projects/web": ["index.html", "style.css"]
        }

        # Создаем структуру уровня 1
        for folder in folders_l1:
            folder_name = folder[:-1]
            new_dir = VFSNode(folder_name, is_directory=True)
            new_dir.parent = self.root
            self.root.children[folder_name] = new_dir
            self.root.content[folder_name] = new_dir

        for filename, content in files_l1.items():
            new_file = VFSNode(filename, is_directory=False, content=content)
            new_file.parent = self.root
            self.root.children[filename] = new_file
            self.root.content[filename] = content

        # Создаем структуру уровня 2
        for parent_folder, subfolders in folders_l2.items():
            if parent_folder in self.root.children:
                parent_node = self.root.children[parent_folder]
                for folder in subfolders:
                    folder_name = folder[:-1]
                    new_dir = VFSNode(folder_name, is_directory=True)
                    new_dir.parent = parent_node
                    parent_node.children[folder_name] = new_dir
                    parent_node.content[folder_name] = new_dir

        for parent_folder, file_list in files_l2.items():
            if parent_folder in self.root.children:
                parent_node = self.root.children[parent_folder]
                for filename in file_list:
                    content = f"Содержимое файла {filename} в папке {parent_folder}"
                    new_file = VFSNode(filename, is_directory=False, content=content)
                    new_file.parent = parent_node
                    parent_node.children[filename] = new_file
                    parent_node.content[filename] = content

        # Создаем структуру уровня 3
        for folder_path, file_list in files_l3.items():
            path_parts = folder_path.split('/')
            current_node = self.root

            # Находим узел для пути
            for part in path_parts:
                if part in current_node.children:
                    current_node = current_node.children[part]

            for filename in file_list:
                content = f"Содержимое файла {filename} в папке {folder_path}"
                new_file = VFSNode(filename, is_directory=False, content=content)
                new_file.parent = current_node
                current_node.children[filename] = new_file
                current_node.content[filename] = content

        self.loaded_items_count = (len(folders_l1) + len(files_l1) +
                                   sum(len(subs) for subs in folders_l2.values()) +
                                   sum(len(files) for files in files_l2.values()) +
                                   sum(len(files) for files in files_l3.values()))
        print(f"Создана VFS с {self.loaded_items_count} элементами и 3 уровнями вложенности")

    def change_directory(self, path):
        """Изменяет текущую директорию в VFS"""
        if path == "/":
            self.current_dir = self.root
            return True

        if path == ".." or path == "../":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
            return True

        if path.startswith("/"):
            target_dir = self._resolve_absolute_path(path)
        else:
            target_dir = self._resolve_relative_path(path)

        if target_dir and target_dir.is_directory:
            self.current_dir = target_dir
            return True
        return False

    def _resolve_absolute_path(self, path):
        """Разрешает абсолютный путь в VFS"""
        path_parts = [p for p in path.split('/') if p]
        current = self.root

        for part in path_parts:
            if part == "..":
                if current.parent:
                    current = current.parent
                continue
            if part == ".":
                continue

            if part in current.children:
                current = current.children[part]
            else:
                return None

        return current

    def _resolve_relative_path(self, path):
        """Разрешает относительный путь в VFS"""
        path_parts = [p for p in path.split('/') if p]
        current = self.current_dir

        for part in path_parts:
            if part == "..":
                if current.parent:
                    current = current.parent
                continue
            if part == ".":
                continue

            if part in current.children:
                current = current.children[part]
            else:
                return None

        return current

    def list_directory(self, path=None):
        """Возвращает список содержимого директории"""
        target_dir = self.current_dir
        if path:
            if path.startswith("/"):
                target_dir = self._resolve_absolute_path(path)
            else:
                target_dir = self._resolve_relative_path(path)

        if not target_dir or not target_dir.is_directory:
            return None

        return list(target_dir.children.keys())

    def get_file_content(self, path):
        """Возвращает содержимое файла по указанному пути"""
        if path.startswith("/"):
            target_node = self._resolve_absolute_path(path.lstrip("/"))
        else:
            target_node = self._resolve_relative_path(path)

        if not target_node:
            return None

        if target_node.is_directory:
            return None  # Это директория, а не файл

        return target_node.content

    def get_current_path(self):
        """Возвращает текущий путь в VFS"""
        return self.current_dir.get_path()

    def find_node(self, path):
        """Находит узел по указанному пути"""
        if path.startswith("/"):
            return self._resolve_absolute_path(path.lstrip("/"))
        else:
            return self._resolve_relative_path(path)

    def change_owner(self, path, owner, group=None):
        """Изменяет владельца файла/директории"""
        node = self.find_node(path)
        if not node:
            return False

        node.owner = owner
        if group:
            node.group = group
        return True

# Глобальный объект VFS
vfs = VFS()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Terminal Emulator')
    parser.add_argument('--vfs-path', help='Путь к физическому расположению VFS')
    parser.add_argument('--startup-script', help='Путь к стартовому скрипту')
    return parser.parse_args()


# === КОМАНДЫ РЕАЛЬНОЙ ФАЙЛОВОЙ СИСТЕМЫ ===

def do_parc(args, output_func):
    """Парсер переменных окружения"""
    if not args:
        output_func("parc: missing variable name")
        return

    var_name = args[0]
    if os.getenv(var_name) is not None:
        output_func(os.getenv(var_name))
    else:
        output_func(f"parc: ${var_name}: variable not found")


def do_vfs_chown(args, output_func):
    """Команда chown для VFS - изменение владельца файла/директории"""
    if not vfs.loaded:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")
        return

    if len(args) < 2:
        output_func("vfs-chown: missing operand")
        output_func("Usage: vfs-chown OWNER FILE")
        output_func("       vfs-chown OWNER:GROUP FILE")
        return

    target = args[-1]  # Последний аргумент - целевой файл/директория
    owner_spec = args[0]

    # Парсим спецификацию владельца (user или user:group)
    if ':' in owner_spec:
        owner, group = owner_spec.split(':', 1)
    else:
        owner = owner_spec
        group = None

    # Находим целевой узел
    if target.startswith("/"):
        target_node = vfs._resolve_absolute_path(target.lstrip("/"))
    else:
        target_node = vfs._resolve_relative_path(target)

    if not target_node:
        output_func(f"vfs-chown: cannot access '{target}': No such file or directory")
        return

    # Меняем владельца
    target_node.owner = owner
    if group:
        target_node.group = group

    output_func(f"Changed ownership of '{target}' to {owner_spec} in VFS")

def do_ls(args, output_func):
    """Команда ls для реальной файловой системы с поддержкой параметров"""
    # Парсим аргументы
    show_all = False
    long_format = False
    target_dir = '.'

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('-'):
            if 'a' in arg:
                show_all = True
            if 'l' in arg:
                long_format = True
        else:
            target_dir = arg
        i += 1

    try:
        entries = os.listdir(target_dir)

        # Фильтруем скрытые файлы если не указан -a
        if not show_all:
            entries = [e for e in entries if not e.startswith('.')]

        # Сортируем - сначала директории, потом файлы
        entries.sort(key=lambda x: (not os.path.isdir(os.path.join(target_dir, x)), x))

        for entry in entries:
            full_path = os.path.join(target_dir, entry)
            if os.path.isdir(full_path):
                if long_format:
                    # Для директории в длинном формате
                    stat_info = os.stat(full_path)
                    mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    permissions = get_permissions_string(stat_info)
                    output_func(
                        f"{permissions} {stat_info.st_nlink:>4} {stat_info.st_uid:>6} {stat_info.st_gid:>6} {'<DIR>':>8} {mtime} {entry}/")
                else:
                    output_func(entry + "/")
            else:
                if long_format:
                    # Для файла в длинном формате
                    stat_info = os.stat(full_path)
                    mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    size = stat_info.st_size
                    permissions = get_permissions_string(stat_info)
                    output_func(
                        f"{permissions} {stat_info.st_nlink:>4} {stat_info.st_uid:>6} {stat_info.st_gid:>6} {size:>8} {mtime} {entry}")
                else:
                    output_func(entry)

    except FileNotFoundError:
        output_func(f"ls: cannot access '{target_dir}': No such file or directory")
    except PermissionError:
        output_func(f"ls: cannot open directory '{target_dir}': Permission denied")


def get_permissions_string(stat_info):
    """Возвращает строку прав доступа в UNIX-стиле"""
    permissions = ''

    # Тип файла
    if stat.S_ISDIR(stat_info.st_mode):
        permissions += 'd'
    else:
        permissions += '-'

    # Права владельца
    permissions += 'r' if stat_info.st_mode & stat.S_IRUSR else '-'
    permissions += 'w' if stat_info.st_mode & stat.S_IWUSR else '-'
    permissions += 'x' if stat_info.st_mode & stat.S_IXUSR else '-'

    # Права группы
    permissions += 'r' if stat_info.st_mode & stat.S_IRGRP else '-'
    permissions += 'w' if stat_info.st_mode & stat.S_IWGRP else '-'
    permissions += 'x' if stat_info.st_mode & stat.S_IXGRP else '-'

    # Права остальных
    permissions += 'r' if stat_info.st_mode & stat.S_IROTH else '-'
    permissions += 'w' if stat_info.st_mode & stat.S_IWOTH else '-'
    permissions += 'x' if stat_info.st_mode & stat.S_IXOTH else '-'

    return permissions

def do_help(args, output_func):
    output_func("Доступные команды:")
    output_func("  Основные: ls, cd, pwd, echo, cat, tail, whoami, exit")
    output_func("  Переменные окружения ($ЗНАЧЕНИЕ)")
    output_func("  VFS: vfs-load, vfs-ls, vfs-cd, vfs-pwd, vfs-cat, vfs-tail, vfs-whoami, vfs-status")
    output_func("  Скрипты: basic_commands, navigation, error_test")
    output_func("  VFS-скрипты: vfs_deepstruct_test, vfs_error_test, vfs_all_test")
    output_func("  Скрипт для проверки всей системы: system_test")
    output_func("  Скрипт этапа 4: stage4_test")
    output_func("  Скрипт этапа 5: stage5_test")
    output_func("")

def do_cd(args, output_func):
    """Команда cd для реальной файловой системы"""
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
    """Команда pwd для реальной файловой системы"""
    output_func(os.getcwd())


def do_echo(args, output_func):
    """Команда echo"""
    output_func(' '.join(args))


def do_cat(args, output_func):
    """Команда cat для реальной файловой системы"""
    if not args:
        output_func("cat: missing file operand")
        return

    filename = args[0]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            output_func(content)
    except FileNotFoundError:
        output_func(f"cat: {filename}: No such file or directory")
    except IsADirectoryError:
        output_func(f"cat: {filename}: Is a directory")
    except Exception as e:
        output_func(f"cat: {filename}: Error reading file")


def do_tail(args, output_func):
    """Команда tail - вывод последних строк файла"""
    if not args:
        output_func("tail: missing file operand")
        output_func("Usage: tail [-n LINES] FILE")
        return

    # Параметры по умолчанию
    lines_count = 10
    filename = None

    # Парсим аргументы
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-n':
            if i + 1 < len(args):
                try:
                    lines_count = int(args[i + 1])
                    i += 1  # Пропускаем следующий аргумент (число строк)
                except ValueError:
                    output_func(f"tail: invalid number of lines: '{args[i + 1]}'")
                    return
            else:
                output_func("tail: option requires an argument -- 'n'")
                return
        elif arg.startswith('-') and len(arg) > 1 and arg[1:].isdigit():
            # Формат -5 (без пробела)
            lines_count = int(arg[1:])
        elif not arg.startswith('-'):
            filename = arg
        i += 1

    if not filename:
        output_func("tail: missing file operand")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()

        # Выводим последние lines_count строк
        start_line = max(0, len(all_lines) - lines_count)
        for line in all_lines[start_line:]:
            output_func(line.rstrip())

    except FileNotFoundError:
        output_func(f"tail: cannot open '{filename}' for reading: No such file or directory")
    except IsADirectoryError:
        output_func(f"tail: error reading '{filename}': Is a directory")
    except Exception as e:
        output_func(f"tail: error reading '{filename}': {str(e)}")


def do_whoami(args, output_func):
    """Команда whoami - вывод текущего пользователя"""
    output_func(os.getlogin())


# === КОМАНДЫ VFS ===

def do_vfs_ls(args, output_func):
    """Команда ls для VFS"""
    if not vfs.loaded:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")
        return

    # Парсим аргументы
    show_all = False
    long_format = False
    target_path = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('-'):
            if 'a' in arg:
                show_all = True
            if 'l' in arg:
                long_format = True
        else:
            target_path = arg
        i += 1

    items = vfs.list_directory(target_path)
    if items is None:
        output_func(f"vfs-ls: cannot access '{target_path}': No such file or directory")
        return

    if not items:
        output_func("(директория пуста)")
        return

    # Фильтруем скрытые файлы если не указан -a
    if not show_all:
        items = [item for item in items if not item.startswith('.')]

    for item in items:
        node = vfs.current_dir.children[item]
        if node.is_directory:
            if long_format:
                # Для директории в длинном формате VFS
                output_func(f"d--------- {node.owner} {node.group} {item}/")
            else:
                output_func(item + "/")
        else:
            if long_format:
                # Для файла в длинном формате VFS
                content_length = len(node.content) if node.content else 0
                output_func(f"---------- {node.owner} {node.group} {content_length:>8} {item}")
            else:
                output_func(item)


def do_vfs_cd(args, output_func):
    """Команда cd для VFS"""
    if not vfs.loaded:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")
        return

    if not args:
        vfs.current_dir = vfs.root
        output_func("Перешел в корень VFS")
        return

    path = args[0]
    if not vfs.change_directory(path):
        output_func(f"vfs-cd: no such file or directory: {path}")


def do_vfs_pwd(args, output_func):
    """Команда pwd для VFS"""
    if not vfs.loaded:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")
        return

    output_func(vfs.get_current_path())


def do_vfs_cat(args, output_func):
    """Команда cat для VFS"""
    if not vfs.loaded:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")
        return

    if not args:
        output_func("vfs-cat: missing file operand")
        return

    filename = args[0]
    if filename in vfs.current_dir.children:
        node = vfs.current_dir.children[filename]
        if not node.is_directory:
            if node.content:
                output_func(node.content)
            else:
                output_func("(файл пуст)")
        else:
            output_func(f"vfs-cat: {filename}: Is a directory")
    else:
        output_func(f"vfs-cat: {filename}: No such file or directory")


def do_vfs_tail(args, output_func):
    """Команда tail для VFS - вывод последних строк файла"""
    if not vfs.loaded:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")
        return

    if not args:
        output_func("vfs-tail: missing file operand")
        output_func("Usage: vfs-tail [-n LINES] FILE")
        return

    # Параметры по умолчанию
    lines_count = 10
    filename = None

    # Парсим аргументы
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-n':
            if i + 1 < len(args):
                try:
                    lines_count = int(args[i + 1])
                    i += 1  # Пропускаем следующий аргумент (число строк)
                except ValueError:
                    output_func(f"vfs-tail: invalid number of lines: '{args[i + 1]}'")
                    return
            else:
                output_func("vfs-tail: option requires an argument -- 'n'")
                return
        elif arg.startswith('-') and len(arg) > 1 and arg[1:].isdigit():
            # Формат -5 (без пробела)
            lines_count = int(arg[1:])
        elif not arg.startswith('-'):
            filename = arg
        i += 1

    if not filename:
        output_func("vfs-tail: missing file operand")
        return

    if filename in vfs.current_dir.children:
        node = vfs.current_dir.children[filename]
        if not node.is_directory:
            if node.content:
                # Разбиваем содержимое на строки
                all_lines = node.content.split('\n')
                # Выводим последние lines_count строк
                start_line = max(0, len(all_lines) - lines_count)
                for line in all_lines[start_line:]:
                    output_func(line)
            else:
                output_func("(файл пуст)")
        else:
            output_func(f"vfs-tail: {filename}: Is a directory")
    else:
        output_func(f"vfs-tail: {filename}: No such file or directory")


def do_vfs_whoami(args, output_func):
    """Команда whoami для VFS - вывод текущего пользователя"""
    output_func(vfs_name)


def do_vfs_load(args, output_func):
    """Команда для загрузки VFS"""
    global vfs_path

    if not args:
        # Загружаем образцовую структуру по умолчанию
        if vfs.load_from_directory(None):
            output_func("VFS загружена (образцовая структура)")
            output_func(f"Загружено элементов: {vfs.loaded_items_count}")
        else:
            output_func("Ошибка загрузки VFS")
    else:
        # Загружаем из реальной директории
        vfs_path = args[0]
        if vfs.load_from_real_directory(vfs_path):
            output_func(f"VFS загружена из: {vfs_path}")
            output_func(f"Загружено элементов: {vfs.loaded_items_count}")
        else:
            output_func(f"Ошибка загрузки VFS из: {vfs_path}")

def do_vfs_status(args, output_func):
    """Команда для показа статуса VFS"""
    if vfs.loaded:
        output_func(f"VFS загружена из: {vfs_path}")
        output_func(f"Элементов в VFS: {vfs.loaded_items_count}")
        output_func(f"Текущий путь в VFS: {vfs.get_current_path()}")
    else:
        output_func("VFS не загружена. Используйте 'vfs-load' для загрузки.")


# === СКРИПТЫ ===

def get_script_path(script_name):
    """Возвращает абсолютный путь к скрипту"""
    # Если указан абсолютный путь, используем его
    if os.path.isabs(script_name):
        return script_name

    # Если указано расширение .txt, ищем как есть
    if script_name.endswith('.txt'):
        # Сначала проверяем в текущей директории
        if os.path.exists(script_name):
            return os.path.abspath(script_name)
        # Затем в директории скриптов
        script_path = os.path.join(script_dir, script_name)
        if os.path.exists(script_path):
            return script_path

    # Если не указано расширение, добавляем .txt
    script_name_with_ext = f"{script_name}.txt"

    # Сначала проверяем в текущей директории
    if os.path.exists(script_name_with_ext):
        return os.path.abspath(script_name_with_ext)

    # Затем в директории скриптов
    script_path = os.path.join(script_dir, script_name_with_ext)
    if os.path.exists(script_path):
        return script_path

    return None


def run_script(script_name, output_widget, output_func):
    """Выполняет скрипт из файла"""
    script_path = get_script_path(script_name)

    if not script_path:
        output_func(f"Скрипт '{script_name}' не найден")
        output_func(f"Искали в: {script_dir} и {os.getcwd()}")
        return False

    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        output_func(f"=== Выполнение скрипта {os.path.basename(script_path)} ===")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue

            # Выводим команду (имитация ввода пользователя)
            output_widget.config(state=tk.NORMAL)
            output_widget.insert(tk.END, f"{vfs_name}$ {line}\n")
            output_widget.config(state=tk.DISABLED)
            output_widget.see(tk.END)
            output_widget.update()

            # Выполняем команду
            result = execute_command(line, output_widget, show_command=False)
            if result == "exit":
                output_func("Скрипт прерван командой exit")
                return True

        output_func(f"=== Скрипт {os.path.basename(script_path)} завершен ===")
        return True

    except Exception as e:
        output_func(f"Ошибка выполнения скрипта: {e}")
        return False


def execute_command(command, output_widget, show_command=True):
    """Выполняет команду и выводит результат в виджет"""
    if show_command:
        output_widget.config(state=tk.NORMAL)
        output_widget.insert(tk.END, f"{vfs_name}$ {command}\n")
        output_widget.config(state=tk.DISABLED)
        output_widget.see(tk.END)
        output_widget.update()

    parts = shlex.split(command)
    if not parts:
        return

    cmd = parts[0]
    args = parts[1:]

    # Функция для вывода в текстовый виджет
    def output_func(text):
        output_widget.config(state=tk.NORMAL)
        output_widget.insert(tk.END, f"{text}\n")
        output_widget.config(state=tk.DISABLED)
        output_widget.see(tk.END)
        output_widget.update()

    # Обработка переменных окружения
    if cmd.startswith('$'):
        do_parc([cmd[1:]], output_func)
    # Команды реальной файловой системы
    elif cmd == exit_cmd:
        return "exit"
    elif cmd == 'ls':
        do_ls(args, output_func)
    elif cmd == 'cd':
        do_cd(args, output_func)
    elif cmd == 'pwd':
        do_pwd(args, output_func)
    elif cmd == 'echo':
        do_echo(args, output_func)
    elif cmd == 'cat':
        do_cat(args, output_func)
    elif cmd == 'tail':
        do_tail(args, output_func)
    elif cmd == 'whoami':
        do_whoami(args, output_func)
    # Команды VFS
    elif cmd == 'vfs-ls':
        do_vfs_ls(args, output_func)
    elif cmd == 'vfs-cd':
        do_vfs_cd(args, output_func)
    elif cmd == 'vfs-pwd':
        do_vfs_pwd(args, output_func)
    elif cmd == 'vfs-cat':
        do_vfs_cat(args, output_func)
    elif cmd == 'vfs-tail':
        do_vfs_tail(args, output_func)
    elif cmd == 'vfs-whoami':
        do_vfs_whoami(args, output_func)
    elif cmd == 'vfs-load':
        do_vfs_load(args, output_func)
    elif cmd == 'vfs-status':
        do_vfs_status(args, output_func)
    elif cmd == 'vfs-chown':
        do_vfs_chown(args, output_func)
    elif cmd == 'help':
        do_help(args, output_func)
    # Запуск скриптов
    elif cmd in ['basic_commands', 'navigation', 'error_test',
                 'vfs_deepstruct_test', 'vfs_error_test',
                 'vfs_all_test', 'system_test', 'stage4_test', "stage5_test"]:
        run_script(cmd, output_widget, output_func)
    else:
        output_func(f'{cmd}: command not found')


def main():
    # Парсим аргументы командной строки
    args = parse_arguments()

    global vfs_path, startup_script
    vfs_path = args.vfs_path
    startup_script = args.startup_script

    # Автоматически загружаем VFS если указан путь
    if vfs_path:
        vfs.load_from_real_directory(vfs_path)

    # Создаем главное окно
    root = tk.Tk()
    root.title(f"Эмулятор - [{os.getlogin()}]")
    root.configure(bg='black')

    # Создаем текстовое поле для вывода
    output_text = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        bg='black',
        fg='white',
        insertbackground='white',
        font=('Courier', 10),
        height=25,
        width=80,
        state=tk.DISABLED
    )
    output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    # Функция для вывода в текстовый виджет
    def output_func(text):
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, f"{text}\n")
        output_text.config(state=tk.DISABLED)
        output_text.see(tk.END)

    # Создаем поле для ввода команды
    input_frame = tk.Frame(root, bg='black')
    input_frame.pack(fill=tk.X, padx=5, pady=5)

    prompt_label = tk.Label(
        input_frame,
        text=f"{vfs_name}$ ",
        bg='black',
        fg='green',
        font=('Courier', 10, 'bold')
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
        command = command_entry.get().strip()
        command_entry.delete(0, tk.END)

        if command:
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