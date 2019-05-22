import argparse
import inspect
import time
import sys


class xcmds(object):
    """
    Translate functions into commands
    """
    def __init__(self, callable_dict:dict, exclude:list = None, include:list=None, log=True):
        """
        :param callable_dict: a dict, {'function name': 'function_object', ...}.Usually it is result of locals()
        :param exclude: a list, do not translate functions in it
        :param include: a list, only translate functions in it
        :param log: if save command line into a log file
        """
        self.log = log
        callable_dict = {x: y for x, y in callable_dict.items() if callable(y)}
        exclude = set(exclude) if exclude else set()
        exclude.add('xcmds')
        if include is not None:
            callable_dict = {k: v for k, v in callable_dict.items() if k in include}
        _ = [callable_dict.pop(x) for x in exclude if x in callable_dict]
        self.run(callable_dict)

    def description2dict(self, description):
        """
        this will only work with doc string in pycharm style
        :param description: docstring
        :return:
        """
        split_docstring = description.strip().split(':param', 1)
        desc_dict = dict()
        if len(split_docstring) == 2:
            # docstring in pycharm style
            summary, arg_spec = split_docstring
            desc_dict['summary'] = summary.strip()
            arg_spec = ':param' + arg_spec
            for line in arg_spec.split('\n'):
                line = line.strip()
                if line.startswith(':param'):
                    arg_name, arg_detail = line.split(':param', 1)[1].split(":", 1)
                    desc_dict[arg_name.strip()] = arg_detail
                elif line.startswith(':return:'):
                    arg_name = 'return'
                    arg_detail = line.split(':return:', 1)[1]
                    desc_dict[arg_name] = arg_detail
                else:
                    desc_dict[arg_name.strip()] += '\n' + line
            else:
                return desc_dict
        else:
            return dict()

    def introduce_command(self, func):
        if isinstance(func, type):
            description = func.__init__.__doc__
        else:
            description = func.__doc__
        desc_dict = self.description2dict(description)
        if desc_dict:
            description = None
        if '-h' not in sys.argv or '--help' in sys.argv or '-help' in sys.argv:
            description = None
        if description:
            _ = [print(x.strip()) for x in description.split('\n') if x.strip()]
            parser = argparse.ArgumentParser(add_help=False)
        else:
            if desc_dict:
                description = desc_dict['summary']
            parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=description)
        parser.prog = func.__name__
        func_args = inspect.getfullargspec(func)
        arg_names = func_args.args
        if not arg_names:
            func()
            if self.log:
                try:
                    with open("cmd." + parser.prog + '.' + str(time.time()) + ".txt", 'w') as f:
                        f.write(' '.join(sys.argv) + '\n')
                except IOError:
                    print('Current Directory may be not writable, thus argument log is not written !')
            return
        arg_defaults = func_args.defaults
        if not arg_defaults:
            arg_defaults = []
        arg_defaults = ['None']*(len(arg_names) - len(arg_defaults)) + list(arg_defaults)
        sig = inspect.signature(func)
        for arg, value in zip(arg_names, arg_defaults):
            if arg == 'self':
                continue
            help_info = desc_dict[arg] if arg in desc_dict else ''
            arg_type = sig.parameters[arg].annotation
            if value == 'None':
                if arg_type in [list, tuple, set]:
                    parser.add_argument('-' + arg, nargs='+', required=True, metavar=arg, help=help_info)
                elif arg_type in [int, str, float]:
                    parser.add_argument('-' + arg, type=arg_type, required=True, metavar=arg, help=help_info)
                else:
                    parser.add_argument('-'+arg, required=True, metavar=arg, help=help_info)
            elif type(value) == bool:
                if value:
                    parser.add_argument('--'+arg, action="store_false", help=help_info or 'default: True')
                else:
                    parser.add_argument('--'+arg, action="store_true", help=help_info or 'default: False')
            elif value is None:
                if arg_type in [list, tuple, set]:
                    parser.add_argument('-' + arg, nargs='+', required=False, metavar=arg, help=help_info)
                elif arg_type in [int, str, float]:
                    parser.add_argument('-' + arg, type=arg_type, required=False, metavar=arg, help=help_info)
                else:
                    parser.add_argument('-'+arg, required=False, metavar='Default:' + str(value), help=help_info)
            else:
                if arg_type in [list, tuple, set] or (type(value) in [list, tuple, set]):
                    default_value = ' '.join(str(x) for x in value)
                    if type(value) in [list, tuple]:
                        one_value = value[0]
                    else:
                        one_value = value.pop()
                    parser.add_argument('-' + arg, default=value, nargs='+', type=type(one_value),
                                        metavar='Default:'+default_value, help=help_info)
                else:
                    parser.add_argument('-' + arg, default=value, type=type(value),
                                        metavar='Default:' + str(value), help=help_info)
        if func_args.varargs is not None:
            print("warning: *varargs is not supported, and will be neglected! ")
        if func_args.varkw is not None:
            print("warning: **keywords args is not supported, and will be neglected! ")
        args = parser.parse_args().__dict__
        if self.log:
            try:
                with open("cmd." + parser.prog + '.' + str(time.time()) + ".txt", 'w') as f:
                    f.write(' '.join(sys.argv) + '\n')
                    f.write('Detail Argument Value:\n'+str(args)+'\n')
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

