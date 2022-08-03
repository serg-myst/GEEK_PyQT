from tabulate import tabulate
from lesson_1_task_2 import host_range_ping
from lesson_1_task_1 import TAB


def host_range_ping_tab():
    host_range_ping(False)


if __name__ == "__main__":
    host_range_ping_tab()
    print(tabulate(TAB, headers='keys', tablefmt='grid', stralign='center'))
