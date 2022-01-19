server package
==============


Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов.

Использование

Модуль подерживает аргементы командной стороки:

1. -p - Порт на котором принимаются соединения
2. -a - Адрес с которого принимаются соединения.
3. --no_gui Запуск только основных функций, без графической оболочки.

* В данном режиме поддерживается только 1 команда: exit - завершение работы.

Примеры использования:

``python server.py -p 8080``

*Запуск сервера на порту 8080*

``python server.py -a localhost``

*Запуск сервера принимающего только соединения с localhost*

``python server.py --no-gui``

*Запуск без графической оболочки*

server.py
~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

server.server module
--------------------

.. automodule:: server.server
   :members:
   :undoc-members:
   :show-inheritance:

Submodules
----------

server.add\_user module
-----------------------

.. automodule:: server.add_user
   :members:
   :undoc-members:
   :show-inheritance:

server.config\_window module
----------------------------

.. automodule:: server.config_window
   :members:
   :undoc-members:
   :show-inheritance:

server.core module
------------------

.. automodule:: server.core
   :members:
   :undoc-members:
   :show-inheritance:

server.database module
----------------------

.. automodule:: server.database
   :members:
   :undoc-members:
   :show-inheritance:

server.main\_window module
--------------------------

.. automodule:: server.main_window
   :members:
   :undoc-members:
   :show-inheritance:

server.remove\_user module
--------------------------

.. automodule:: server.remove_user
   :members:
   :undoc-members:
   :show-inheritance:


server.stat\_window module
--------------------------

.. automodule:: server.stat_window
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: server
   :members:
   :undoc-members:
   :show-inheritance:
