from abc import ABC, abstractmethod
import argparse
import inspect

from components import Component


class MyHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """ Custom help formatter for argparse. """

    def _get_default_metavar_for_optional(self, action):
        if action.type is None:
            return ""
        return action.type.__name__

    def _get_default_metavar_for_positional(self, action):
        if action.type is None:
            return ""
        return action.type.__name__


class CLI:
    def __init__(self, description=""):
        self.commands = dict()
        self.parser = argparse.ArgumentParser(description=description)
        self.subparsers = self.parser.add_subparsers(
            help="Select one of the following subcommands:",
            dest='command',
            metavar="subcommand"
        )
        self.subparsers.required = True

    def __call__(self):
        self.run()

    def run(self):
        if len(self.commands) > 0:
            self.setup()
            cls, kwargs = self.parse_args()
            obj = cls.resolve(**kwargs)
            obj.run()

    @property
    def Command(self):
        class Command(ABC):
            """ Resolves parameters from command line arguments. """

            def __init_subclass__(cls, **kwargs):
                """ Hooks the subclass as a runnable command. """
                super().__init_subclass__(**kwargs)
                if not issubclass(cls, Component):
                    raise TypeError("cli.Command should only be used on Components")
                self.commands[cls.__name__] = cls

            @abstractmethod
            def run(self):
                pass

        return Command

    def setup(self):
        for cls in self.commands.values():
            self.setup_command(cls)

    def setup_command(self, cls):
        sub_parser = self.subparsers.add_parser(
            cls.__name__,
            help=cls.__doc__,
            description=cls.__doc__,
            formatter_class=MyHelpFormatter
        )

        def add_bool_param(parser, *names, dest, default):
            """
            Add boolean parameter as two flags (--name/--no-name).
            default indicates default value or None for a required boolean parameter.
            """
            required = default is None
            group = parser.add_mutually_exclusive_group(required=required)
            group.add_argument(*names, help="(default)" if default is True else "", dest=dest,
                               action='store_true')
            # strip dashes and add '--no-'
            no_names = [f"--no-{name[2 if name[:2] == '--' else 1:]}" for name in names]
            group.add_argument(*no_names, help="(default)" if default is False else "",
                               dest=dest, action='store_false')
            if default is not None:
                group.set_defaults(**{dest: default})

        def format_name(name):
            param_name = name.replace('_', '-')
            prefix = "-" if len(param_name) == 1 else "--"
            return prefix + param_name

        required_arguments = sub_parser.add_argument_group('required arguments')
        for param in cls.get_requested_params(flatten=True):
            required = param.default is inspect.Parameter.empty
            names = [format_name(alias) for alias in sorted(param.aliases, key=len) if not (alias.startswith('_'))]
            if required:
                p = required_arguments
            else:
                p = sub_parser

            if param.type == bool:
                add_bool_param(p, *names, dest=param.full_name, default=None if required else param.default)
            else:
                conditional_kwargs = dict()
                if not required:
                    conditional_kwargs['default'] = param.default
                    conditional_kwargs['help'] = "(default: %(default)s)"
                p.add_argument(*names,
                               type=param.type,
                               dest=param.full_name,
                               required=required,
                               **conditional_kwargs)

    def parse_args(self):
        cmd_args = self.parser.parse_args()
        fName = cmd_args.command
        cls = self.commands[fName]

        kwargs = {n: v for n, v in cmd_args._get_kwargs() if n != "command"}

        return cls, kwargs
