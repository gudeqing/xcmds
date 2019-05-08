xcmds
-----
* pip install xcmds
* example.py:
```
from xcmds import xcmds

ddef func(a=1, b=2):
    print(a*b)


def func2(a='x', b=3):
    print([a]*b)


if __name__ == '__main__':
    xcmds(locals())

python example.py func -a 199

```

See [document](https://gudeqing.github.io/xcmds/ "With a Title").
