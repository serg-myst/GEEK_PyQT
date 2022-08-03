from ipaddress import ip_address
from lesson_1_task_1 import host_ping


def host_range_ping(on_print=True):
    list_ip = []

    start_adr = input('Введите первоначальный IP-адрес (например 8.8.8.0): ')

    list_oct = start_adr.split('.')
    try:
        if list_oct[3] != '0':
            print('Некорректно введен IP-адрес. Последняя цифра октета должна быть 0!')
            return
    except ValueError:
        print('Некорректно введен IP-адрес')
        return

    check_adr = int(input('Введите количество адресов для проверки (цифры последнего октета от 1 до 255): '))

    if check_adr > 255:
        print('Количество адресов должно быть в диапозоне от 1 до 255')
        return

    for i in range(0, check_adr + 1):
        # ip = ip_address(f'{list_oct[0]}.{list_oct[1]}.{list_oct[2]}.{str(i)}')
        ip = int(ip_address(start_adr)) + i
        list_ip.append(ip_address(ip))

    host_ping(list_ip, on_print)


if __name__ == "__main__":
    host_range_ping()
