from ipaddress import ip_address
import platform
from subprocess import Popen, PIPE
import locale
import threading

PARAMS = '-n' if platform.system().lower() == 'windows' else '-c'
# Поставил cp866 иначе кракозябры выводит. Можно еще проверит на язык windows
ENCODING = 'cp866' if platform.system().lower() == 'windows' else locale.getpreferredencoding()
TAB = []  # Здесь будет список словарей для красивого вывода в задании 3


def host_ping_ip(ip, on_print):
    args = ['ping', PARAMS, '1', ip]  # один раз пинганем
    with Popen(args, stdout=PIPE, stderr=PIPE) as reply:
        code = reply.wait()
        if code == 0:
            TAB.append({'Reachable': ip})
            if on_print:
                print(f'Узел доступен {ip} {reply.stdout.read().decode(ENCODING)}\n')
            return True
        else:
            TAB.append({'Unreachable': ip})
            if on_print:
                print(f'Узел недоступен {ip} {reply.stderr.read().decode(ENCODING)}\n')
            return False


# Используем многопоточность для ускорения работы. Данные получаем сразу, как только завершится самый долгй процесс
# Описание работы с многопоточностью
# https://webdevblog.ru/vvedenie-v-potoki-v-python/
def host_ping(ip_list, on_print=True):
    thread_list = []
    for ip in ip_list:
        thread_list.append(threading.Thread(target=host_ping_ip, args=(str(ip), on_print,)))

    for thread in thread_list:
        thread.start()

    for t in thread_list:
        t.join()


if __name__ == "__main__":
    host_ping([ip_address('8.8.8.8'), ip_address('127.0.0.1'), ip_address('8.0.0.1'), ip_address('8.8.8.1'),
               ip_address('8.8.8.2'), ip_address('8.8.8.3'), ip_address('8.8.8.4'), ip_address('8.8.8.5'),
               ip_address('8.8.8.6'), ip_address('8.8.8.7'), ip_address('8.8.8.9'), ip_address('8.8.8.10')])
