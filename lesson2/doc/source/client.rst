client package
==============


Клиентское приложение для обмена сообщениями. Поддерживает
отправку сообщений пользователям которые находятся в сети, сообщения шифруются
с помощью алгоритма RSA с длинной ключа 2048 bit.

Поддерживает аргументы коммандной строки:

``python client.py {имя сервера} {порт} -n или --name {имя пользователя} -p или -password {пароль}``

1. {имя сервера} - адрес сервера сообщений.
2. {порт} - порт по которому принимаются подключения
3. -n или --name - имя пользователя с которым произойдёт вход в систему.
4. -p или --password - пароль пользователя.

Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо использовать в паре.

Примеры использования:

* ``python client.py``

*Запуск приложения с параметрами по умолчанию.*

* ``python client.py ip_address some_port``

*Запуск приложения с указанием подключаться к серверу по адресу ip_address:port*

* ``python -n test1 -p 123``

*Запуск приложения с пользователем test1 и паролем 123*

* ``python client.py ip_address some_port -n test1 -p 123``

*Запуск приложения с пользователем test1 и паролем 123 и указанием подключаться к серверу по адресу ip_address:port*


client.py
--------------------

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

.. automodule:: client.client
   :members:
   :undoc-members:
   :show-inheritance:


Submodules
----------

client.add\_contact module
--------------------------

.. automodule:: client.add_contact
   :members:
   :undoc-members:
   :show-inheritance:



client.client\_transport module
-------------------------------

.. automodule:: client.client_transport
   :members:
   :undoc-members:
   :show-inheritance:

client.database module
----------------------

.. automodule:: client.database
   :members:
   :undoc-members:
   :show-inheritance:

client.del\_contact module
--------------------------

.. automodule:: client.del_contact
   :members:
   :undoc-members:
   :show-inheritance:

client.main\_window module
--------------------------

.. automodule:: client.main_window
   :members:
   :undoc-members:
   :show-inheritance:

client.main\_window\_conv module
--------------------------------

.. automodule:: client.main_window_conv
   :members:
   :undoc-members:
   :show-inheritance:

client.start\_dialog module
---------------------------

.. automodule:: client.start_dialog
   :members:
   :undoc-members:
   :show-inheritance:

client.temp\_transport module
-----------------------------

.. automodule:: client.temp_transport
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: client
   :members:
   :undoc-members:
   :show-inheritance:
