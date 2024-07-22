import inspect
import warnings
import typing

from components.param import Param, ComponentParam

# backport for typing < 3.8
get_origin = getattr(typing, 'get_origin', lambda x: getattr(x, '__origin__', None))
get_args = getattr(typing, 'get_args', lambda x: getattr(x, '__args__', None))


class Component(object):
    """
    A component is a part of the system. It can request parameters through its __init__ function.
    Components can also consist of other components.
    """

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__params = kwargs
        params = iter(inspect.signature(cls.__init__).parameters.values())
        next(params)  # skip self
        for index, param in enumerate(params):
            # skip keyword args that were already provided
            if param.name in obj.__params:
                continue
            # skip *args and **kwargs
            if param.kind == inspect.Parameter.VAR_POSITIONAL or param.kind == inspect.Parameter.VAR_KEYWORD:
                continue

            # fill in positional arguments
            if index < len(args):
                obj.__params[param.name] = args[index]
            # fill in default values
            else:
                obj.__params[param.name] = param.default

        return obj

    # def __init__(self):
    #     pass

    @property
    def name(self):
        """ A printable name of the component. """
        return self.__class__.__name__

    @property
    def identifier(self):
        """ A printable name of the component that more precisely defines it.
        Default: `self.name(self.get_params_string)`"""
        return f"{self.name}({self.get_params_string(recursive=False)})"

    @property
    def full_identifier(self):
        """ A printable name of the component that completely defines it.
        Default: `self.name(self.get_params_string)`"""
        return f"{self.name}({self.get_params_string(recursive=True)})"

    def get_params_string(self, sep=", ", eq="=", recursive=True, rec_placeholder="..."):
        """ A string representaion of the parameters. Recursive indicates whether subcomponents should be shown. """
        params = list()
        for k, v in self.get_params().items():
            if k.startswith('_'):
                continue
            vs = repr(v)
            if not recursive and isinstance(v, Component):
                vs = f"{v.name}({rec_placeholder})"
            if not recursive and isinstance(v, tuple):
                vs = sep.join([f"{vv.name}({rec_placeholder})" for vv in v])
                vs = f"({vs})"
            params.append(f"{k}{eq}{vs}")
        return sep.join(params)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.identifier

    @classmethod
    def get_requested_params(cls, flatten=False):
        """
        Returns a list of parameters for this component.
        Component parameters are hierarchical and contain parameters of subcomponents.
        Each param includes its type, default value from __init__ and alternative names.
        """
        current_component_param = cls._get_requested_params(dict(), dict(), [])
        if flatten:
            return current_component_param.flatten()
        return current_component_param.params

    @classmethod
    def _get_requested_params(cls, parent_provided_types, parent_provided_params, prefixes):
        """
        Returns a ComponentParam of this component.
        This hierarchical structure includes their type and default value from __init__ or get_provided_params and
        additionally, alternative names are provided.
        """
        # first do a pass to resolve names
        params = cls._resolve_requested_names(prefixes)

        # check consistency
        current_component_param = ComponentParam("__main__", cls, None, params=params)
        current_component_param.enforce_consistency()

        # Then do a pass to resolve types
        current_component_param.params = cls._update_requested_types(params, parent_provided_types,
                                                                     parent_provided_params, prefixes)
        return current_component_param

    @classmethod
    def _resolve_requested_names(cls, parent_aliases):
        requested = list()

        # Skip auto generated init (contains "args")
        if cls.__init__ == object.__init__:
            return list()

        param_iter = iter(inspect.signature(cls.__init__).parameters.items())
        next(param_iter)  # skip self
        for parname, iparam in param_iter:
            # fetch type via typing module to resolve forward refs
            tpe = typing.get_type_hints(cls.__init__).get(parname, inspect.Parameter.empty)

            # filter out Optional[tpe] conversion performed by get_type_hints
            if get_origin(tpe) == typing.Union:
                args = get_args(tpe)
                if len(args) == 2 and args[1] == None.__class__:
                    tpe = args[0]
            default = iparam.default

            # if no type provided, try to derive it from original default value
            if tpe == inspect.Parameter.empty:
                if default != inspect.Parameter.empty and default is not None:
                    tpe = type(default)
                else:
                    tpe = None

            # if type is Tuple[], treat as tuple of parameters
            if get_origin(tpe) == tuple or get_origin(tpe) == typing.Tuple:
                # check against typing.Tuple (Python3.6) and tuple (Python 3.7 onward)
                tpe = ComponentList(tpe.__args__)
                if default == inspect.Parameter.empty:
                    default = list()

            # compute aliases of param
            if parname.startswith('_'):
                # if non-identifying, only compute aliases with real name
                aliases = {prefix + '_' + parname[1:] for prefix in parent_aliases}
                aliases.add(parname[1:])
                aliases.add(parname)
            else:
                aliases = {prefix + '_' + parname for prefix in parent_aliases}
                aliases.add(parname)

            tpe_is_comp = tpe is not None and isinstance(tpe, type) and issubclass(tpe, Component)
            if tpe_is_comp:
                param = ComponentParam(parname, tpe, default, aliases=aliases)
                param.params = tpe._resolve_requested_names(aliases)
            else:
                param = Param(parname, tpe, default, aliases)

            requested.append(param)

        return requested

    @classmethod
    def _update_requested_types(cls, params, parent_provided_types, parent_provided_params, prefixes):
        provided_types = cls.get_provided_types()
        provided_types.update(parent_provided_types)

        provided_params = cls.get_provided_parameters()
        provided_params.update(parent_provided_params)

        for param in params:
            # set default value to provided parameter
            if param.aliases & provided_params.keys():
                key = param.aliases & provided_params.keys()
                if len(key) > 1:
                    raise TypeError(
                        f"Attribute override for parameter {param.full_name} supplied multiple times: {key}")
                key = list(key)[0]
                param.default = provided_params.pop(key)

            # Change type based on type hint in annotation
            if provided_types.keys() & param.aliases:
                old_type = param.type
                key = param.aliases & provided_types.keys()
                if len(key) > 1:
                    raise TypeError(
                        f"Type for parameter {param.full_name} supplied multiple times: {key}")
                key = list(key)[0]
                new_type = provided_types.pop(key)

                # if type is Tuple[], treat as tuple of parameters
                if get_origin(new_type) == tuple or get_origin(new_type) == typing.Tuple:
                    new_type = ComponentList(new_type.__args__)

                param.type = new_type

                old_is_comp = old_type is not None and isinstance(old_type, type) and issubclass(old_type, Component)
                new_is_comp = issubclass(param.type, Component)
                if old_is_comp != new_is_comp:
                    raise TypeError(f"Tried to change type {old_type} into {param.type}, which isn't allowed.")

                # if component type changed, refresh hierarchy
                if new_is_comp:
                    sub_params = param.type._get_requested_params(provided_types, provided_params,
                                                                  prefixes + [param.name]).params
                    param.params = sub_params
            elif isinstance(param, ComponentParam):
                param.type._update_requested_types(param.params, provided_types, provided_params,
                                                   prefixes + [param.name])

        return params

    @classmethod
    def get_provided_parameters(cls):
        """ Returns provided parameters as a dict.
        """
        attributes = {name: getattr(cls, name) for name in dir(cls)}
        attributes = {name: var for name, var in attributes.items() if
                      not (callable(var) or isinstance(var, property)) and not name.startswith('__')}
        return attributes

    @classmethod
    def get_provided_types(cls):
        """ Returns provided parameter types as a dict.
        """
        types = dict()
        for c in list(cls.__bases__) + [cls]:
            types.update(typing.get_type_hints(c))
        return types

    def resolve_provided_params(self, requested_params):
        pass

    @classmethod
    def resolve(cls, **params):
        """
        Resolves the components and subcomponents recursively.
        Uses `cls.get_provided_parameters` first to set default values, then overrides with strict **params.
        """
        requested_params = cls.get_requested_params()
        object = cls._resolve(params, dict(), requested_params)

        # Check if all params were used
        if len(params) > 0:
            raise TypeError(f"Unexpected parameter(s): {params}")

        return object

    @classmethod
    def _resolve(cls, params, parent_provided_params, requested_params):
        """
        Resolves the components and subcomponents recursively.
        Uses `provided_params` first to set default values, then overrides with params.
        Need to pop from params to check if they were all used.
        """
        provided_params = cls.get_provided_parameters()
        provided_params.update(parent_provided_params)
        kwargs = dict()
        for requested_param in requested_params:
            found = False
            value = None
            # Try to find it in the user params
            if requested_param.aliases & params.keys():
                found = True
                key = requested_param.aliases & params.keys()
                if len(key) > 1:
                    raise TypeError(f"Value for parameter {requested_param.full_name} supplied multiple times: {key}")
                key = list(key)[0]
                value = params.pop(key)
            # In the case of a component: see if the type is a component and try to resolve it.
            elif requested_param.type is not None and issubclass(
                    requested_param.type, Component):
                # param is of type ComponentParam
                found = True
                value = requested_param.type._resolve(params, provided_params, requested_param.params)
            # No parameter found? No worries, there is a default
            elif requested_param.default is not inspect.Parameter.empty:
                found = True
                value = requested_param.default

            if found:
                if requested_param.type is not None and not issubclass(
                        requested_param.type, _ComponentList):
                    if not isinstance(value, requested_param.type):
                        # warn for type mismatch, except for trivial cases:
                        if (requested_param.default is None and value is None) or (requested_param.type == float and type(value) == int):
                            pass
                        else:
                            warnings.warn(
                                f"Parameter '{requested_param.full_name}' expected type {requested_param.type}, but got {type(value)} instead",
                                RuntimeWarning)
                kwargs[requested_param.name] = value
            else:
                # no default and no provided parameter: can't instantiate component.
                #  error will be raised when trying to instantiate.
                warnings.warn(f"Missing parameter for resolve: {requested_param.name}", RuntimeWarning)
        return cls(**kwargs)

    def get_params(self):
        """ Returns a dictionary of the parameters and their values that were supplied through __init__. """
        return self.__params


class _ComponentList(Component):
    """ Helper class to parse Tuple[Component, ...] type params. Don't use this directly. """
    def __new__(cls, *args, **kwargs):
        """ Hack to change creation type of this class back to tuple """
        comps = [None] * len(kwargs)
        for index, comp in kwargs.items():
            comps[int(index)] = comp
        return tuple(comps)

    @staticmethod
    def comp_types():
        raise NotImplementedError("comp_types has to be implemented by subclass")

    @classmethod
    def _resolve_requested_names(cls, parent_aliases):
        requested = list()
        for index, tpe in enumerate(cls.comp_types()):
            if tpe == Component:
                # Filter out base Component type
                continue

            if tpe == Ellipsis:
                # Variadic type given, means don't fill in components
                return []

            # if type is Tuple[], treat as list
            if get_origin(tpe) == tuple or get_origin(tpe) == typing.Tuple:
                tpe = ComponentList(tpe.__args__)

            name = str(index)

            # compute aliases of param
            aliases = {prefix + '_' + name for prefix in parent_aliases}
            aliases.add(name)

            if tpe is not None and issubclass(tpe, Component):
                param = ComponentParam(name, tpe, inspect.Parameter.empty, aliases=aliases)
                param.params = tpe._resolve_requested_names(aliases)
            else:
                param = Param(name, tpe, inspect.Parameter.empty, aliases)

            requested.append(param)

        return requested


def ComponentList(component_types):
    """ Helper class to parse Tuple[Component, ...] type params. Don't use this directly. """

    class C(_ComponentList):
        @staticmethod
        def comp_types():
            return component_types

    return C

# TODO: Add decorator for explicit parameters overrides.
#       This makes it possible to provide a warning for class attributes that were unused (might indicate name change or typo)
