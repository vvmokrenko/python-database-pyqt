"""Программа-клиент"""
from socket import socket
import sys
import json
import time
import argparse
import threading
import logs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from transport import Transport
from decorators import logc, log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from metaclasses import ClientVerifier

class Client(Transport, metaclass=ClientVerifier):
    """
    Класс определеят свойства и методы для клиента.
    """
    # для работы проверки класса в метаклассе
    # aaaa = socket()

    def __init__(self, ipaddress, port, client_name):
        self.LOGGER = Transport.set_logger_type('client')
        super().__init__(ipaddress, port)
        self.ipaddress = self.ipaddress or DEFAULT_IP_ADDRESS
        self.client_name = client_name
        """Сообщаем о запуске"""
        print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {self.client_name}')
        # Если имя пользователя не было задано, необходимо запросить пользователя.
        if not self.client_name:
            self.client_name = input('Введите имя пользователя: ')

        self.LOGGER.info(
            f'Запущен клиент с парамертами: адрес сервера: {self.ipaddress}, '
            f'порт: {self.port}, имя пользователя: {self.client_name}')

    @logc
    def init(self):
        """
        Метод инициализации клиента
        :return:
        """
        try:
            self.socket.connect((self.ipaddress, self.port))
        except ServerError as error:
            self.LOGGER.error(f'Не удалось соединиться с сервером по адресу {self.ipaddress} на порту {self.port}. '
                              f'Сервер вернул ошибку {error.text}')
            return -1
        except ConnectionRefusedError:
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            return -1
        self.LOGGER.info(f'Клиент соединился с сервером {self.socket}')

    @logc
    def message_from_server(self, sock, my_username):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = self.get(sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    self.LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                     f'\n{message[MESSAGE_TEXT]}')
                else:
                    self.LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                self.LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                self.LOGGER.critical(f'Потеряно соединение с сервером.')
                break

    @logc
    def create_message(self, sock, account_name='Guest'):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        :param sock:
        :param account_name:
        :return:
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        self.LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            self.send(sock, message_dict)
            self.LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception:
            self.LOGGER.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @logc
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.send(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                self.LOGGER.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @logc
    def create_presence(self, account_name='Guest'):
        """
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        """
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        self.LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @logc
    def process_message(self, message):
        """
        Функция разбирает ответ сервера
        :param message:
        :return:
        """

        self.LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @staticmethod
    @log
    def arg_parser():
        """Создаём парсер аргументов коммандной строки
        и читаем параметры, возвращаем 3 параметра
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-n', '--name', default=None, nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        server_address = namespace.addr
        server_port = namespace.port
        client_mode = namespace.name

        return server_address, server_port, client_mode

    @logc
    def run(self):
        """
            Обработчик событий от сервера
            :return:
        """

        try:
            message_to_server = self.create_presence(self.client_name)
            self.send(self.socket, message_to_server)
            self.LOGGER.info(f'Послалали сообщение на сервер {message_to_server}')
            answer = self.process_message(self.get(self.socket))
            self.LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            # print(answer)
        except (ValueError, json.JSONDecodeError):
            self.LOGGER.error('Не удалось декодировать сообщение сервера.')
            sys.exit(1)
        except ServerError as error:
            self.LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            self.LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                              f'{missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            self.LOGGER.critical(
                f'Не удалось подключиться к серверу {self.ipaddress}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # запускаем клиенский процесс приёма сообщний
            receiver = threading.Thread(target=self.message_from_server, args=(self.socket, self.client_name))
            receiver.daemon = True
            receiver.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.
            user_interface = threading.Thread(target=self.user_interactive, args=(self.socket, self.client_name))
            user_interface.daemon = True
            user_interface.start()
            self.LOGGER.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


def main():
    """
    Загружаем параметы коммандной строки.
    Делаем проверку на IndexError.
    Проверки на ValueError будут внутри классов.
    """
    server_address, server_port, client_name = Client.arg_parser()

    # Инициализация сокета и обмен
    clnt = Client(server_address, server_port, client_name)
    # Если не прошли проверку на ValueError выходим из программы
    if clnt == -1:
        sys.exit(1)
    # Соединяемся с сервером
    if clnt.init() == -1:
        sys.exit(1)
    # Осуществляем обмен сообщениями
    clnt.run()


if __name__ == '__main__':
    main()
