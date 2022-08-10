# Lesson_2 Добавим дескриптор
class CheckPort:

    # def __init__(self, my_attr):
    #    self.my_attr = my_attr

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('Порт должен быть больше или равно 0!!!')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name