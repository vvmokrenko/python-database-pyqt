"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен
быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность
с выводом соответствующего сообщения («Узел доступен»,
«Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться
с помощью функции ip_address().
2. Написать функцию host_range_ping() для перебора ip-адресов из
заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам
проверки должно выводиться соответствующее сообщение.
3. Написать функцию host_range_ping_tab(), возможности которой основаны
на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
и выглядеть примерно так:
Reachable
10.0.0.1
10.0.0.2
Unreachable
10.0.0.3
10.0.0.4
"""

import platform
from subprocess import Popen, PIPE
from ipaddress import ip_address
import socket
import ipaddress
from tabulate import tabulate
import threading

PARAM = '-n' if platform.system().lower() == 'windows' else '-c'

def ip_address(host):
    """
    Функция возвращает IP-адрес по входящему имени,
    которое может быть представлено ip-адресом, именем хоста, ip-адресом в виде числа.
    В случае невозможности определения адреса возвращаем False
    """
    try:
        if type(host) in (str, int):
            IPV4 = str(ipaddress.ip_address(host))
        else:
            return False
    except ValueError:
        try:
            IPV4 = socket.gethostbyname(host)
        except socket.gaierror:
            return False
    return IPV4



def host_ping(lst, print_flag=False):
    """
    Фукция проверки доступности сетевых узлов
    """
    result = dict()
    for host in lst:
        if print_flag: print(f'Проверяем хост {host} ... ', end='')
        verified_ip = ip_address(host)
        if verified_ip:
            args = ['ping', PARAM, '1', verified_ip]
            reply = Popen(args, stdout=PIPE, stderr=PIPE)

            code = reply.wait()
            if code == 0:
                if print_flag: print(f'Доступен. IP-адрес {verified_ip}')
                result[host] = ('Доступен', verified_ip)
            else:
                if print_flag: print(f'Не доступен. IP-адрес {verified_ip}')
                result[host] = ('Не доступен', verified_ip)
        else:
            if print_flag: print(f'Не определен')
            result[host] = ('Не определен',)

    return result

def ping(host, verified_ip, result, print_flag=False):
    args = ['ping', PARAM, '1', verified_ip]
    reply = Popen(args, stdout=PIPE, stderr=PIPE)

    code = reply.wait()
    if code == 0:
        if print_flag:
            print(f'Хост {host} доступен. IP-адрес {verified_ip}')
        result[host] = ('Доступен', verified_ip)
    else:
        if print_flag:
            print(f'Хост {host} не доступен. IP-адрес {verified_ip}')
        result[host] = ('Не доступен', verified_ip)

def host_ping_thread(lst, print_flag=False):
    """
    Фукция проверки доступности сетевых узлов, реализованная через потоки
    """
    threads = []
    result = dict()
    for host in lst:
        verified_ip = ip_address(host)
        if verified_ip:
            thread = threading.Thread(target=ping, args=(host, verified_ip, result, print_flag), daemon=True)
            thread.start()
            threads.append(thread)
        else:
            if print_flag:
                print(f'Хост {host} не определен')
            result[host] = (f'Не определен',)

    for thread in threads:
        thread.join()

    return result


def host_range_ping(start_address, add_no, print_flag=False):
    """
    Функция, начиная с заданного ip-адреса, проверяет доступность этого адреса и ip-адресов
    с изменением последнего октета на количество адресов, равное add_no
    """
    check = host_ping([start_address])[start_address]
    if check[0] != 'Не определен':
        oktets = list(map(int, check[1].split('.')))
        last_oktet = oktets[-1]
        if last_oktet + add_no > 255:
            print(f'Указанное кол-во переборов {add_no} для стартового адресf {start_address} '
                  f'превышает допустимое число 255 для последнего октета')
        else:
            address_list = [f'{oktets[0]}.{oktets[1]}.{oktets[2]}.{last_oktet + i}' for i in range(add_no)]
            return host_ping_thread(address_list, print_flag)
    else:
        print(f'Входящий адрес {start_address} не определен')


def host_range_ping_tab(start_address, add_no):
    """
    Функция выводит в табличном виде результаты работы функции host_range_ping
    """
    table = [('Доступные', 'Недоступные')]
    sort = [[], []]

    address_list = host_range_ping(start_address, add_no, False)
    sort[0] = [key for key, value in address_list.items() if value[0] == 'Доступен']
    sort[1] = [key for key, value in address_list.items() if value[0] != 'Доступен']
    table.extend(list(zip(*sort)))
    if len(sort[0]) > len(sort[1]):
        for item in sort[0][len(sort[1]):]:
            table.append((item, None))
    elif len(sort[0]) < len(sort[1]):
        for item in sort[1][len(sort[0]):]:
            table.append((None, item))

    print(tabulate(table, headers='firstrow', tablefmt='pipe'))


address_list = ['www.rbc.ru', 'www.unknown.ru', '10.15.23.100',
                'www.sports.ru', '123.34.223.112', 3232235776, 'unknown', '10.234.11.156']

print('---------------------------------Задание №1-------------------------------------', end='\n\n')
# Вариант без использования потоков. Работает дольше
# host_ping(address_list, True)
# Вариант с использованием потоков. Работает существенно быстрее
host_ping_thread(address_list, True)
print('\n---------------------------------Задание №2-------------------------------------', end='\n\n')
address = input('Введите ip-адрес или имя хоста: ')
ip_no = int(input('Введите количество ip-адресов для перебора: '))
host_range_ping(address, ip_no, True)
print('\n---------------------------------Задание №3-------------------------------------', end='\n\n')
host_range_ping_tab(address, ip_no)