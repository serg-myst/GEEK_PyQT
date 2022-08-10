# Lesson_2

# Библиотека dis позволяет разобрать код на атрибуты, методы, классы и т.д.
# Описание: https://docs.python.org/3/library/dis.html
import dis


def create_lists(attrs):
    # LOAD_GLOBAL - обычные методы, которые используются в фукнциях класса
    # LOAD_METHOD - обычные меотды, обернутые декоратором
    # LOAD_ATTR - атрибуты, используемые в функциях класса

    methods_load_global = []
    methods_load_method = []
    attributes = []

    for f in attrs:
        try:
            res = dis.get_instructions(attrs[f])
        except TypeError:
            pass
        else:
            for r in res:  # обход полученных атрибутов
                if r.opname == 'LOAD_GLOBAL':
                    if r.argval not in methods_load_global:
                        methods_load_global.append(r.argval)
                elif r.opname == 'LOAD_METHOD':
                    if r.argval not in methods_load_method:
                        methods_load_method.append(r.argval)
                elif r.opname == 'LOAD_ATTR':
                    if r.argval not in attributes:
                        attributes.append(r.argval)

    return methods_load_global, methods_load_method, attributes


class ServerVerifier(type):

    def __init__(cls, future_class_name, future_class_parent, future_class_attrs):
        # Разложим по массивам методы и атрибуты. Потом проанализируем.

        # Проверка зна сокеты TCP
        check_tcp_sockets = ['AF_INET', 'SOCK_STREAM']
        check_methods = ['connect']

        methods_load_global, methods_load_method, attributes = create_lists(future_class_attrs)

        # Проверка использования сокетов для работы по TCP
        check_list = list(filter(lambda i: i in attributes, check_tcp_sockets))
        if check_list != check_tcp_sockets:
            raise RuntimeError('Для работы по TCP должны использоваться "AF_INET", "SOCK_STREAM"')

        # Проверка на наличие методов connect
        check_list = list(filter(lambda i: i in methods_load_global, check_methods))
        if len(check_list) != 0:
            raise RuntimeError('Для сервера не допустимо наличие методов "connect"')

        # Для отладки оставлю.
        # print(20 * '=')
        # print(methods_load_global)
        # print(20 * '=')
        # print(methods_load_method)
        # print(20 * '=')
        # print(attributes)

        super().__init__(future_class_name, future_class_parent, future_class_attrs)


class ClientVerifier(type):

    def __init__(cls, future_class_name, future_class_parent, future_class_attrs):
        # Проверка зна сокеты TCP
        check_tcp_sockets = ['sock']  # Уже содержит transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        check_methods = ['accept', 'listen']

        methods_load_global, methods_load_method, attributes = create_lists(future_class_attrs)

        # Проверка использования сокетов для работы по TCP
        check_list = list(filter(lambda i: i in attributes, check_tcp_sockets))
        if check_list != check_tcp_sockets:
            raise RuntimeError('Для работы по TCP должны использоваться "AF_INET", "SOCK_STREAM"')

        # Проверка на наличие методов accept, listen
        check_list = list(filter(lambda i: i in methods_load_global, check_methods))
        if len(check_list) != 0:
            raise RuntimeError('Для клиента не допустимо наличие методов "accept", "listen"')

        # Для отладки оставлю.
        # print(20 * '=')
        # print(methods_load_global)
        # print(20 * '=')
        # print(methods_load_method)
        # print(20 * '=')
        # print(attributes)

        super().__init__(future_class_name, future_class_parent, future_class_attrs)