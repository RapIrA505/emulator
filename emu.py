import shlex

vfs_name = "docker$ "
exit_cmd = "exit"

while True:
    command = input(vfs_name)
    parts = shlex.split(command)


    if command == exit_cmd:
        break
    if len(parts) == 0:
        continue
    if parts[0] == 'ls':
        print(parts[0])
    elif parts[0] == 'cd':
        print(parts[0])
    else:
        print(f'{command}: command not found')