import datajoint as dj
import inspect

class SchemaTemplate:

    """
    A schema object is a decorator for datajoint pipeline classes
    """

    def __init__(self, upstream_table_names=None,
                 required_method_names=None):
        """
        :param required_table_names: names of tables the current pipeline requires
        :param required_method_names: names of methods the current pipeline requires
        """

        self.upstream_table_names = upstream_table_names
        self.required_method_names = required_method_names
        self._table_classes = []


    @property
    def requirements(self):
        """
        return: a message as a guidance for users to generate proper requirements
        """
        if not (self.upstream_table_names or self.required_method_names):
            return 'No required upstream tables or methods.'

        msg = '"requirements" needs to be a dictionary with'

        if self.upstream_table_names:
            msg += ' - Keys for upstream tables: {}'.format(self.upstream_table_names)
        if self.required_method_names:
            msg += ' - Keys for require methods: {}'.format(self.required_method_names)

        return msg

    def _check_requirements(self, requirements):

        checked_requirements = {}
        if self.upstream_table_names:
            for k in self.upstream_table_names:
                if k not in requirements:
                    raise KeyError('Requiring upstream table: {}'.format(k))
                else:
                    checked_requirements[k] = requirements[k]

        if self.required_method_names:
            for k in self.required_method_names:
                if k not in requirements or not inspect.isfunction(requirements[k]):
                    raise KeyError('Requiring method: {}'.format(k))
                else:
                    checked_requirements[k] = requirements[k]

        return checked_requirements

    def __call__(self, table_class, context=None):
        '''
        While decorating, add table classes into self.tables
        '''
        if not context:
            context = inspect.currentframe().f_back.f_locals

        self._table_classes.append(table_class)


    def declare_tables(self, schema, requirements=None, context=None, add_here=False):
        """
        Method to declare tables in a datajoint pipeline in a schema
        :param schema: the schema object to decorate this pipeline
        :param requirements: a dictionary listing required tables and required methods
        :param context: dictionary for looking up foreign key references, leave None to use local context.
        :param add_here: True if adding the alias of class objects into the current context
        :return: initiated tables as a dictionary in the format of {class.__name__: class object}
        """
        requirements = self._check_requirements(requirements)

        if not context:
            context = inspect.currentframe().f_back.f_locals

        tables = {}
        for table_class in self._table_classes:

            if requirements:
                for hook_name, hook_target in requirements.items():
                    hook_name = '_{}'.format(hook_name)
                    if hook_name in dir(table_class):
                        setattr(table_class, hook_name, hook_target)

            print('Initializing {}'.format(table_class.__name__))
            table = schema(table_class, context=context)
            context[table.__name__] = table
            setattr(self, table.__name__, table)

        if add_here:
            context.update(**tables)
