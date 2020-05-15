import datajoint as dj
import inspect

class Pipeline:

    def __init__(self, table_classes,
                 required_table_names=None,
                 required_method_names=None):

        self._table_classes = table_classes
        self.requried_table_names = required_table_names
        self.requried_method_names = required_method_names

    @property
    def requirements(self):

        if not (self.requried_table_names or self.requried_method_names):
            return 'No required upstream tables or methods.'

        msg = u'"requirements" needs to be a dictionary with'

        if self.requried_table_names:
            msg += u' - Keys for upstream tables: {}'.format(self.requried_table_names)
        if self.requried_method_names:
            msg += u' - Keys for require methods: {}'.format(self.requried_method_names)

        return msg

    def _check_requirements(self, requirements=None):
        if not requirements:
            raise KeyError(self.requirements)

        checked_requirements = {}
        for k in self.requried_table_names:
            if k not in requirements:
                raise KeyError(f'Requiring upstream table: {k}')
            else:
                checked_requirements[k] = requirements[k]

        if self.requried_method_names:
            for k in self.requried_method_names:
                if k not in requirements or not inspect.isfunction(requirements[k]):
                    raise KeyError(f'Requiring method: {k}')
                else:
                    checked_requirements[k] = requirements[k]

        return checked_requirements

    def _init_tables(self, schema, context):
        tables = {}
        for table_class in self._table_classes:
            print(f'Initializing {table_class.__name__}')
            table = schema(table_class, context=context)
            context[table.__name__] = table
            tables[table.__name__] = table

        return tables

    def init_pipeline(self, schema, context={}, add_here=False):
        if add_here and not context:
            context = inspect.currentframe().f_back.f_locals

        tables = self._init_tables(schema, context)
        pipeline = {**tables}

        if add_here:
            context.update(**pipeline)

        return pipeline