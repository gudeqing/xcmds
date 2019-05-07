from xcmds import xcmds
from pprint import pprint as print


def func(a=1, b=2):
    print(a*b)


def func2(a='x', b=3):
    print([a]*b)


if __name__ == '__main__':
    xcmds(locals(), exclude=['print'], log=True)
