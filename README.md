xcmds
-----
* pip install dist/*gz

* example.py:
```
def func(a=1, b=2):
    print(a*b)


def func2(a='x', b=3):
    print([a]*b)


if __name__ == '__main__':
    from xcmds import xcmds
    xcmds.xcmds(locals())

python example.py func -a 199

```

See [document](https://gudeqing.github.io/xcmds/ "With a Title").
