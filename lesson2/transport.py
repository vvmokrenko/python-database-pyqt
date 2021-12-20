"""
Общий предок для клиента и сервера.
"""
import socket
from abc import ABC, abstractmethod
from message import Message
import logging
import time
from common.variables import ACTION, TIME, ACCOUNT_NAME, EXIT
from descrptrs import Port
from metaclasses import ServerVerifier, TransportVerifier


# class Transport(ABC):
class Transport(metaclass=TransportVerifier):
    """
    Класс определеят общие свойства и методы для клиента и сервера.
    """
    LOGGER = logging.getLogger('')  # инициализируем атрибут класса
    # Валидация значения порта через дескриптор
    port = Port()

    # # Валидация значения порта через метод __new__ (рабочий код)
    # def __new__(cls, *args, **kwargs):
    #     try:
    #         port = int(args[1])
    #         if port < 1024 or port > 65535:
    #             raise ValueError
    #     except ValueError:
    #         cls.LOGGER.critical(
    #             f'Попытка запуска клиента с неподходящим номером порта: {port}.'
    #             f' Допустимы адреса с 1024 до 65535')
    #         return -1
    #     except IndexError:
    #         cls.LOGGER.critical('Не указан номер порта.')
    #         return -1
    #     #  если значения параметров корреткны создаем объект
    #     return super().__new__(cls)

    def __init__(self, ipaddress, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipaddress = ipaddress
        self.port = int(port)
        self.LOGGER.info(f'Создан объект типа {type(self)}, присвоен сокет {self.socket}')

    # Сокет для обмена сообщениями
    @property
    def socket(self):
        """ Получаем сокет"""
        return self.__socket

    # Инициализация сервера/клента
    # @abstractmethod
    def init(self):
        pass

    # Запуск сервера/клиента
    # @abstractmethod
    def run(self):
        pass

    # Обработать сообщение (послать или получить в зависимости от типа транспорта)
    # @abstractmethod
    def process_message(self, message):
        pass

    # Послать сообщение адресвту
    @staticmethod
    def send(tosocket, message):
        Message.send(tosocket, message)

    # Принять сообщение от адресвта
    @staticmethod
    def get(fromsocket):
        return Message.get(fromsocket)

    # Возвращает рабочий набор ip-адреса и порта
    @property
    def connectstring(self):
        return (self.ipaddress, self.port)

    # Устнавливаеи тип логгера в зависимости от функции (клиент или сервер)
    @classmethod
    def set_logger_type(cls, logtype):
        cls.LOGGER = logging.getLogger(logtype)
        return cls.LOGGER

    @staticmethod
    def create_exit_message(account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @staticmethod
    def print_help():
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')
