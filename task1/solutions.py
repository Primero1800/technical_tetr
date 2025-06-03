"""
Необходимо реализовать декоратор `@strict`
Декоратор проверяет соответствие типов переданных в вызов функции аргументов типам аргументов, объявленным в прототипе функции.
(подсказка: аннотации типов аргументов можно получить из атрибута объекта функции `func.__annotations__` или с помощью модуля `inspect`)
При несоответствии типов бросать исключение `TypeError`
Гарантируется, что параметры в декорируемых функциях будут следующих типов: `bool`, `int`, `float`, `str`
Гарантируется, что в декорируемых функциях не будет значений параметров, заданных по умолчанию
"""

import inspect


def strict(func):
    def wrapper(*args, **kwargs):
        types = inspect.signature(func).parameters
        types_keys = list(types.keys())
        for i, arg in enumerate(args):
            key = types_keys[i]
            if not isinstance(arg, types.get(key).annotation):
                raise TypeError
        for key, value in kwargs.items():
            if not isinstance(value, types.get(key).annotation):
                raise TypeError
        return func(*args, **kwargs)
    return wrapper


@strict
def sum_two(a: int, b: int) -> int:
    return a + b


@strict
def sum_three(a: int, b: float, c:bool) -> float:
    return b + a + c


# print(sum_two(1, 2))  # >>> 3
# print(sum_two(1, 2.4))  # >>> TypeError


if __name__ == "__main__":
    print(sum_three(1, 3.2, c=True))
    # print(sum_three(1,  True, c=3.2))
    print(sum_three(c=False, a=2, b=2.3))

    print(sum_two(1, 2))  # >>> 3
    print(sum_two(1, 2.4))  # >>> TypeError
