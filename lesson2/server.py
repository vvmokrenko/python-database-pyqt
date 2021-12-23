"""Программа-сервер"""

import sys
import argparse
import select
import logs.config_server_log
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, \
    USER, ACCOUNT_NAME, SENDER, PRESENCE, ERROR, MESSAGE, \
    MESSAGE_TEXT, RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from transport import Transport
from decorators import log, logc
from metaclasses import ServerVerifier
from server_database import ServerStorage
import threading

class Server(Transport,  metaclass=ServerVerifier):
    """
    Класс определеят свойства и методы для сервера
    """

    def __init__(self, ipaddress, port, database):
        self.LOGGER = Transport.set_logger_type('server')
        super().__init__(ipaddress, port)
        # База данных сервера
        self.database = database
        self.LOGGER.info(f'Сервер подключаем по адресу {ipaddress} на порту {port}')

    @logc
    def init(self):
        self.socket.bind(self.connectstring)
        self.socket.settimeout(0.5)
        # Слушаем порт
        self.socket.listen(MAX_CONNECTIONS)
        self.LOGGER.info('Сервер начал слушать порт')
        self.clients = []
        self.messages = []
        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        self.names = dict()

    @logc
    def process_client_message(self, message, messages_list, client):
        """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
        проверяет корректность, отправляет словарь-ответ в случае необходимости.
        :param message:
        :param messages_list:
        :param client:
        :return:
        """

        self.LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                self.send(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                self.send(client, response)
                self.clients.remove(client)
                client.close()
            return

        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return

        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:

            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return

        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            self.send(client, response)
            return

    @logc
    def process_message(self, message, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        :param message:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            self.send(self.names[message[DESTINATION]], message)
            self.LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                             f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            self.LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    @logc
    def run(self):
        """
        Обработчик событий от клиента
        :return:
        """
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                self.LOGGER.info(f'Установлено соедение с ПК {client_address}')
                # Добавляем клиента в список в конец
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(self.get(client_with_message),
                                                    self.messages, client_with_message)
                    except Exception as e:
                        self.LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                         f'отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            for i in self.messages:
                try:
                    self.process_message(i, send_data_lst)
                except Exception:
                    self.LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[i[DESTINATION]])
                    del self.names[i[DESTINATION]]
            self.messages.clear()

    @staticmethod
    @log
    def arg_parser():
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        listen_port = namespace.p

        return listen_address, listen_port

def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключённых пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = Server.arg_parser()

    # Инициализация базы данных
    database = ServerStorage()

    # Создание экземпляра класса - сервера и его запуск:
    srv = Server(listen_address, listen_port, database)
    # Если не прошли проверку на ValueError выходим из программы
    if srv == -1:
        sys.exit(1)
    # Инициализируем листенер
    srv.init()

    # # Непонятно как вызвать super у классов с разными конструкторами
    # srv.daemon = True
    # srv.start()

    # # Начинаем принимать сообщения
    # srv.run()
    #

    # Печатаем справку:
    print_help()

    # Основной цикл сервера:
    while True:
        command = input('Введите команду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
