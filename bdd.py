class Feature:

    class Background:
        
        def __init__(self):
            self.conditions = []

        def addCondition(self, condition, *args, **kwargs):
            self.conditions.append((condition, args, kwargs))
        
        def getConditions(self):
            return self.conditions

    def __init__(self, name):
        self.name = name
        self.scenarios = []
        self.background = None

    def setBackground(self, b):
        if self.background is not None:
           raise Exception("Background already defined")

        if len(self.scenarios) > 0:
           raise Exception("Background must be defined before Scenarios")

        self.background = b

    def addScenario(self, s):
        self.scenarios.append(s)

    def test(self):
        print("Testing feature {}".format(self.name))
        for s in self.scenarios:
            s.run()
 
class Assertion:

    @staticmethod
    def Is(expected, actual):
        return expected == actual

    @staticmethod
    def IsNot(expected, actual):
        return expected != actual

class Scenario:

    def __init__(self, feature, title):
        self.feature = feature
        self.title = title
        self.conditions = []
        self.events = []
        self.clauses = []
        self.args_map = {}
        self.values = [()]

        if feature.background:
            self.conditions.extend(feature.background.conditions)

    def addCondition(self, condition, *args, **kwargs):
        if not condition.__call__:
            raise ValueError("Condition must be a callable")

        self.conditions.append((condition, args, kwargs))
    
    def addEvent(self, event, *args, **kwargs):
        if not event.__call__:
            raise ValueError("Condition must be a callable")

        self.events.append((event, args, kwargs))
    
    def addClause(self, clause, assertion, value, *args, **kwargs):
        if not clause.__call__:
            raise ValueError("Condition must be a callable")

        self.clauses.append((clause, args, kwargs, assertion, value))

    def setValues(self, arg_names, values):

        if self.args_map:
           raise Exception("A Scenario can only have one set of values")

        for index, args in enumerate(values):
            if len(arg_names) != len(args):
                raise ValueError("Value tuple {} does not match number of argument names".format(index))

        self.values = values
        self.args_map = {}
        for arg_pos, arg in enumerate(arg_names):
            if not isinstance(arg, str):
                raise ValueError("Value names must be strings")
            if arg in self.args_map:
                raise ValueError("Value names must be unique: {}".format(arg))
            self.args_map[arg] = arg_pos

    def run(self):

        runs = len(self.values)

        for r in range(runs):
            try:
                values_map = self._map_values(self.args_map, self.values[r])
        
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
        
        if not self.values:
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
