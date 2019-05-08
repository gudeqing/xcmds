from xcmds.xcmds import xcmds
from pprint import pprint as print
from unittest import TestCase


def func(a=1, b=2):
    print(a*b)


def func2(a='x', b=3):
    print([a]*b)


calls = locals()


class XcmdsTest(TestCase):
    def test_xcmds(self):
        xcmds(calls, exclude=['print'], log=True)


if __name__ == '__main__':
    xcmds(locals())
