import argparse
import inspect
import time
import sys


class xcmds(object):
    def __init__(self, callable_dict:dict, exclude:list = None, include:list=None, log=True):
        self.log = log
        callable_dict = {x: y for x, y in callable_dict.items() if callable(y)}
        exclude = set(exclude) if exclude else set()
        exclude.add('xcmds')
        if include is not None:
            callable_dict = {k: v for k, v in callable_dict.items() if k in include}
        _ = [callable_dict.pop(x) for x in exclude if x in callable_dict]
        self.run(callable_dict)

    def introduce_command(self, func):
        if isinstance(func, type):
            description = func.__init__.__doc__
        else:
            description = func.__doc__
        if '-h' not in sys.argv or '--help' in sys.argv or '-help' in sys.argv:
            description = None
        if description:
            _ = [print(x.strip()) for x in description.split('\n') if x.strip()]
            parser = argparse.ArgumentParser(add_help=False)
        else:
            parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=description)
        parser.prog = func.__name__
        func_args = inspect.getfullargspec(func)
        arg_names = func_args.args
        if not arg_names:
            func()
            return
        arg_defaults = func_args.defaults
        if not arg_defaults:
            arg_defaults = []
        arg_defaults = ['None']*(len(arg_names) - len(arg_defaults)) + list(arg_defaults)
        sig = inspect.signature(func)
        for arg, value in zip(arg_names, arg_defaults):
            if arg == 'self':
                continue
            arg_type = sig.parameters[arg].annotation
            if value == 'None':
                if arg_type in [list, tuple, set]:
                    parser.add_argument('-' + arg, nargs='+', required=True, metavar=arg)
                elif arg_type in [int, str, float]:
                    parser.add_argument('-' + arg, type=arg_type, required=True, metavar=arg)
                else:
                    parser.add_argument('-'+arg, required=True, metavar=arg)
            elif type(value) == bool:
                if value:
                    parser.add_argument('--'+arg, action="store_false", help='default: True')
                else:
                    parser.add_argument('--'+arg, action="store_true", help='default: False')
            elif value is None:
                if arg_type in [list, tuple, set]:
                    parser.add_argument('-' + arg, nargs='+', required=False, metavar=arg)
                elif arg_type in [int, str, float]:
                    parser.add_argument('-' + arg, type=arg_type, required=False, metavar=arg)
                else:
                    parser.add_argument('-'+arg, required=False, metavar='Default:' + str(value))
            else:
                if arg_type in [list, tuple, set] or (type(value) in [list, tuple, set]):
                    default_value = ' '.join(str(x) for x in value)
                    if type(value) in [list, tuple]:
                        one_value = value[0]
                    else:
                        one_value = value.pop()
                    parser.add_argument('-' + arg, default=value, nargs='+', type=type(one_value),
                                        metavar='Default:'+default_value, )
                else:
                    parser.add_argument('-' + arg, default=value, type=type(value),
                                        metavar='Default:' + str(value), )
        if func_args.varargs is not None:
            print("warning: *varargs is not supported, and will be neglected! ")
        if func_args.varkw is not None:
            print("warning: **keywords args is not supported, and will be neglected! ")
        args = parser.parse_args().__dict__
        if self.log:
            try:
                with open("cmd." + str(time.time()) + ".txt", 'w') as f:
                    f.write(' '.join(sys.argv) + '\n')
            except IOError:
                print('Current Directory may be not writable, thus argument log is not written !')
        start = time.time()
        func(**args)
        print("total time: {}s".format(time.time() - start))

    def run(self, callable_dict):
        if len(callable_dict) >= 2:
            if len(sys.argv) <= 1:
                print("The tool has the following sub-commands: ")
                _ = [print(x) for x in callable_dict]
                return
            sub_cmd = sys.argv[1]
            sys.argv.remove(sub_cmd)

            if sub_cmd in callable_dict:
                self.introduce_command(callable_dict[sub_cmd])
            else:
                print('sub-command: {} is not defined'.format(sub_cmd))
        elif len(callable_dict) == 1:
            self.introduce_command(callable_dict.pop(list(callable_dict.keys())[0]))
        else:
            raise Exception('No callable object found!')

