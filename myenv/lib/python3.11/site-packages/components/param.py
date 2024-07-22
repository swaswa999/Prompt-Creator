

class Param(object):
    def __init__(self, name, tpe, default, aliases=None):
        # original name of the parameter
        self.name = name
        self.type = tpe
        self.default = default
        # aliases need to be unique within the component hierarchy. ComponentParam.enforce_consistency() checks this.
        if aliases is None:
            self.aliases = {self.name}
        else:
            self.aliases = set(aliases)

    @property
    def minimal_name(self):
        """ Shortest name that still uniquely identifies the parameter. """
        if len(self.aliases) == 0:
            return self.name
        return min(self.aliases, key=len)

    @property
    def full_name(self):
        """ Fully defined name in component hierarchy. """
        if len(self.aliases) == 0:
            return self.name
        return max(self.aliases, key=len)

    def __repr__(self):
        return f"Param: {self.full_name}"

    def remove_invalid_aliases(self):
        str_numbers = set(map(str, range(10)))
        self.aliases = {alias for alias in self.aliases if not alias[0] in str_numbers}

    def _remove_conflicting_aliases(self, name_map):
        for alias in list(self.aliases):
            if alias in name_map:
                # name already defined
                other_param = name_map[alias]
                # use discard iso remove, because it may have already been deleted from the mapped param
                other_param.aliases.discard(alias)
                self.aliases.remove(alias)
                # Note: do not remove param from name_map, because conflict can occur more than 2 times
            else:
                name_map[alias] = self

    def check_valid(self):
        """ Check if parameter still has at least one name. """
        if len(self.aliases) == 0:
            raise AttributeError(f"No valid identifier for parameter {self.name}")

    def flatten(self):
        """ Return flattened version of params, without components. """
        return [self]


class ComponentParam(Param):
    def __init__(self, name, tpe, default, params=None, aliases=None):
        super().__init__(name, tpe, default, aliases=aliases)
        if params is None:
            self.params = list()
        else:
            self.params = params

    def __repr__(self):
        return f"ComponentParam: {self.full_name}"

    def enforce_consistency(self):
        # 1. remove aliases that aren't valid identifiers.
        self.remove_invalid_aliases()
        # 2. remove all shadowed variable names
        self.remove_shadowed_aliases()
        # 3. resolve all conflicting names
        self.remove_conflicting_aliases()
        # 4. if param without valid identifier, raise error
        self.check_valid()

    def remove_invalid_aliases(self):
        """ Remove aliases that aren't valid identifiers. """
        super().remove_invalid_aliases()
        for param in self.params:
            param.remove_invalid_aliases()

    def remove_shadowed_aliases(self):
        """
        Remove all variable names that conflict with a parent name.
        Uses depth first traversal to remove parent names from children.
        """
        self._remove_shadowed_aliases(set())

    def _remove_shadowed_aliases(self, defined):
        all_param_names = self.aliases.copy()
        for param in self.params:
            all_param_names |= param.aliases

        for param in self.params:
            param.aliases -= defined  # prune aliases as well
            if isinstance(param, ComponentParam):
                param._remove_shadowed_aliases(defined | all_param_names)

    def remove_conflicting_aliases(self):
        """
        Remove all names that occur multiple times, without a parent-child relation.
        Uses in-order traversal with map from names to components to detect conflicts.
        """
        name_map = dict()
        self._remove_conflicting_aliases(name_map)

    def _remove_conflicting_aliases(self, name_map):
        super()._remove_conflicting_aliases(name_map)
        for param in self.params:
            param._remove_conflicting_aliases(name_map)

    def check_valid(self):
        """ Check if every parameter still has at least one name. """
        super().check_valid()
        for param in self.params:
            param.check_valid()

    def flatten(self):
        """ Return flattened version of params, without components. """
        return sum(map(lambda x: x.flatten(), self.params), [])


