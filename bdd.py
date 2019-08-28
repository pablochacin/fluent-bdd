class Feature:

    class BackgroundCls:

        class Condition:

            def __init__(self, background):
                self.background = background

            def And(self, condition, *args, **kwargs):
                self.background.conditions.append((condition, args, kwargs))
                return Feature.BackgroundCls.Condition(self.background)

            def Scenario(self, title):
                return self.background.feature.Scenario(title)

         
        def __init__(self, feature):
            self.feature = feature
            self.conditions = []

        def Given(self, condition, *args, **kwargs):
            self.conditions.append((condition, args, kwargs))
            return Feature.BackgroundCls.Condition(self)

    def __init__(self, name):
        self.name = name
        self.scenarios = []
        self.background = None

    def Background(self):
        if self.background is not None:
           raise Exception("Background already defined")

        if len(self.scenarios) > 0:
           raise Exception("Background must be defined before Scenarios")

        self.background = Feature.BackgroundCls(self)
        return self.background

    def Scenario(self, title):
        s = Scenario(self, title)
        self.scenarios.append(s)
        return s

    def Test(self):
        print("Testing feature {}".format(self.name))
        for s in self.scenarios:
            s.Run()
 
class Scenario:

    class Condition:

        def __init__(self, scenario):
           self.scenario = scenario

        def And(self, condition, *args, **kwargs):
            self.scenario.add_condition(condition, args, kwargs)
            return Scenario.Condition(self.scenario)

        def When(self, event, *args, **kwargs):
            self.scenario.add_event(event, args, kwargs)
            return Scenario.Event(self.scenario)

        def Build(self):
            return self.scenario.Test()


    class Event:

        def __init__(self, scenario):
           self.scenario = scenario

        def And(self, event, *args, **kwargs):
            self.scenario.add_event(event, args, kwargs)
            return Scenario.Event(self.scenario)

        def Then(self, clause, *args, **kwargs):
            return Scenario.OpenClause(self.scenario, clause, args, kwargs)

        def Test(self):
            return self.scenario.Test()

    class OpenClause:

        def __init__(self, scenario, clause, args, kwargs):
            self.scenario = scenario
            self.clause = clause
            self.args = args
            self.kwargs = kwargs

        def Is(self, value):
            self.scenario.add_clause(self.clause, self.args, self.kwargs, Scenario.Assertion.Is, value)
            return Scenario.Clause(self.scenario)

        def IsNot(self, value):
            self.scenario.add_clause(self.clause, self.args, self.kwargs, Scenario.Assertion.IsNot, value)
            return Scenario.Clause(self.scenario)

    class Clause:

        def __init__(self, scenario):
           self.scenario = scenario

        def And(self, clause, *args, **kwargs):
            return Scenario.OpenClause(self.scenario, clause, args, kwargs)

        def Test(self):
            self.scenario.Test()

        def Scenario(self, title):
            return self.scenario.feature.Scenario(title)

    class Assertion:

        @staticmethod
        def Is(expected, actual):
            return expected == actual

        @staticmethod
        def IsNot(expected, actual):
            return expected != actual


    def __init__(self, feature, title):
        self.feature = feature
        self.title = title
        self.conditions = []
        self.events = []
        self.clauses = []
        self.args_map = {}
        self.examples = [()]

        if feature.background:
            self.conditions.extend(feature.background.conditions)

    def add_condition(self, condition, args, kwargs):
        if not condition.__call__:
            raise ValueError("Condition must be a callable")

        self.conditions.append((condition, args, kwargs))
    
    def add_event(self, event, args, kwargs):
        if not event.__call__:
            raise ValueError("Condition must be a callable")

        self.events.append((event, args, kwargs))
    
    def add_clause(self, clause, args, kwargs, assertion, value):
        if not clause.__call__:
            raise ValueError("Condition must be a callable")

        self.clauses.append((clause, args, kwargs, assertion, value))
    
    def Given(self, condition, *args, **kwargs):
        self.add_condition(condition, args, kwargs)
        return Scenario.Condition(self)

    def When(self, event, *args, **kwargs):
        self.add_event(event, args, kwargs)
        return Scenario.Event(self)


    def Examples(self, arg_names, examples):

        if self.args_map:
           raise Exception("A Scenario can only have one set of examples")

        for index, args in enumerate(examples):
            if len(arg_names) != len(args):
                raise ValueError("Value tuple {} does not match number of argument names".format(index))

        self.examples = examples
        self.args_map = {}
        for arg_pos, arg in enumerate(arg_names):
            if not isinstance(arg, str):
                raise ValueError("Value names must be strings")
            if arg in self.args_map:
                raise ValueError("Value names must be unique: {}".format(arg))
            self.args_map[arg] = arg_pos

        return self

    def Test(self):
        self.feature.Test()

    def Run(self):

        runs = len(self.examples)

        for r in range(runs):
            try:
                values_map = self._map_values(self.args_map, self.examples[r])
        
                if len(self.events) == 0:
                    raise ValueError("No events specified for scenario {}".format(self.title))
                
                if len(self.clauses) == 0:
                    raise ValueError("No clauses specified for scenario {}".format(self.title))
                
                for condition, args, kwargs in self.conditions:
                    try:
                        self._execute(condition, args, kwargs, values_map)
                    except Exception as ex:
                        condition_str = self._signature(condition, args, kwargs, values_map)
                        raise Exception("Condition {} Failed with error: {}".format(condition_str, ex))

                for event, args, kwargs in self.events:
                    try:
                        self._execute(event, args, kwargs, values_map)
                    except Exception as ex:
                        event_str = self._signature(event, args, kwargs, values_map)
                        raise Exception("Event {} Failed with error: {}".format(event_str, ex))

                for clause, args, kwargs, assertion, value in self.clauses:
                    clause_str = self._signature(clause, args, kwargs, values_map)
                    result = None
                    try:
                        result = self._execute(clause, args, kwargs, values_map)
                    except Exception as ex:
                         raise Exception("Clause {} Failed with error: {}".format(clause_str, ex))

                    assertion_value = self._bind_arg(value, values_map)
                    if not assertion(result, assertion_value):
                        raise Exception("Clause {} {} '{}' Actual '{}' ".format(clause_str, assertion.__name__, assertion_value, result))

                print("Scenario {} success".format(self.title))

            except Exception as ex:
                print("Scenario {} failed: {}".format(self.title, ex))
            finally:
                self.current_run = 0

    def _map_values(self, args_map, values):
        values_map = {}
        for arg_name, pos in args_map.items():
            values_map[arg_name] = values[pos]
        return values_map

    def _execute(self, func, args, kwargs, values_map):
         args_values, kwargs_values = self._bind_args(args, kwargs, values_map)
         return func(*args_values, **kwargs_values)
      
    def _bind_arg(self, arg, values_map):
        # a unbound arg must be a string 
        if not isinstance(arg, str):
            return arg

        left = arg.find('{')
        right = arg.rfind('}')
        if left <0 or right < 0 or right <= left:
             return arg
	
        arg_name = arg[left+1:right]
        try:
            return values_map[arg_name]
        except KeyError:
            raise ValueError("Argument {} not defined".format(arg))

    def _bind_args(self, args, kwargs, values_map):
        
        if not self.examples:
           return args, kwargs

        args_values = []
        for arg in args:
            args_values.append(self._bind_arg(arg, values_map))
        
        kwargs_values = {}
        for arg_name, arg_value in kwargs.items():
            kwargs_values[arg_name] = self._bind_arg(arg_name, values_map)

        return tuple(args_values), kwargs_values

    def _signature(self, function, args, kwargs, values_map):
        args_values, kwargs_values = self._bind_args(args, kwargs, values_map)

        signature = "{}(".format(function.__name__)
        if args:
            signature = signature + (",".join(["%s"]*len(args_values)) % args_values)
        
        if kwargs:
            signature = signature + ','.join('{}={}'.format(k,v) for k,v in kwargs_values.items())
            
        signature = signature+")"

        return signature
