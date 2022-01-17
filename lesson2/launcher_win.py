"""Программа-лаунчер"""

import subprocess
import sys
import os

PROCESSES = []

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


while True:
    ACTION = input(
            'Выберите действие: q - выход , s - запустить сервер, k - запустить клиенты x - закрыть все окна:')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        # Было раньше
        # PROCESSES.append(subprocess.Popen('python server.py',
        #                                   creationflags=subprocess.CREATE_NEW_CONSOLE))
        # PROCESSES.append(subprocess.Popen('python client.py -n test1',
        #                                   creationflags=subprocess.CREATE_NEW_CONSOLE))
        # PROCESSES.append(subprocess.Popen('python client.py -n test2',
        #                                   creationflags=subprocess.CREATE_NEW_CONSOLE))
        # PROCESSES.append(subprocess.Popen('python client.py -n test3',
        #                                   creationflags=subprocess.CREATE_NEW_CONSOLE))
        # Запускаем сервер!
        PROCESSES.append(subprocess.Popen(f"{PYTHON_PATH} {BASE_PATH}/server.py",
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        # with subprocess.Popen(f"{PYTHON_PATH} {BASE_PATH}/server.py",
        #                  creationflags=subprocess.CREATE_NEW_CONSOLE,
        #                  stdout=subprocess.PIPE) as p:
        #     print('sfsfsf', p.stdout.read())
        # # # Запускаем клиентов:
        # for i in range(clients_count):
        #     PROCESSES.append(subprocess.Popen(f"{PYTHON_PATH} {BASE_PATH}/client.py -n test{i + 1}",
        #                                       creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123456.')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
            clients_count = int(
                input('Введите количество тестовых клиентов для запуска: '))
            # Запускаем клиентов:
            for i in range(clients_count):
                # with subprocess.Popen(
                #         f'{PYTHON_PATH} {BASE_PATH}/client.py -n test{i + 1} -p 123456',
                #         creationflags=subprocess.CREATE_NEW_CONSOLE,
                #         stdout=subprocess.PIPE) as p:
                #     #  print('Отладка\n', p.stdout.read())
                #     PROCESSES.append(p)
                PROCESSES.append(subprocess.Popen(
                        f'{PYTHON_PATH} {BASE_PATH}/client.py -n test{i + 1} -p 123456',
                        creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
