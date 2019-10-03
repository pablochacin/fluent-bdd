class Feature:
    """
       A class that represents a BDD Feature.

       A Feature has one or more Scenarios. Each scenario is independent.
       The Scenarios may share a Background, which defines a set of Conditions.
    """

    class Background:
        """
        Defines a set of Conditions shared by the Scenarios in a Feature
        """
        
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

    def addScenario(self, title):
        s = Scenario(title)
        if self.background:
           for func, args, kwargs in self.background.getConditions():
               s.addCondition(func, *args, **kwargs)
        self.scenarios.append(s)
        return s

    def test(self):
        print("Testing feature {}".format(self.name))
        for s in self.scenarios:
            try:
                s.run()
            except Exception as ex:
                print("Exception running scenario '{}': {}".format(s.title, ex))
 
class Assertion:
    """
    Defines the assertions that can be evaluated in a Condition
    """ 

    @staticmethod
    def Is(expected, actual):
        """
        Checks if the expected and actual values are equal.
        """
        return expected == actual

    @staticmethod
    def IsNot(expected, actual):
        """
        Checks if the expected and actual values are not equal
        """
        return expected != actual

class Scenario:
    """
    Defines a BDD scenario. 
   
    A Scenario contains a list of Conditions, followed by a list of
    Events and a list of Assertions. Conditions, Events and Clauses must
    be introduced in order.

    Conditions, Events, and Clauses may reference parameters which take their
    values from a list of Examples. In that case, the Scenario is evaluated for
    each set of values from the Examples.
    """

    def __init__(self, title):
        self.title = title
        self.conditions = []
        self.events = []
        self.clauses = []
        self.args_map = {}
        self.examples = [()]

    def addCondition(self, condition, *args, **kwargs):
        if not condition.__call__:
            raise ValueError("Condition must be a callable")

        self.conditions.append(Scenario.Condition(condition, args, kwargs))
    
    def addEvent(self, event, *args, **kwargs):
        if not event.__call__:
            raise ValueError("Event must be a callable")

        self.events.append(Scenario.Event(event, args, kwargs))
    
    def addClause(self, clause, assertion, value, *args, **kwargs):
        if not clause.__call__:
            raise ValueError("Clause must be a callable")

        self.clauses.append(Scenario.Clause(clause, args, kwargs, assertion, value))


    def setExamples(self, arg_names, examples):

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


    def _getArgsValues(self, values):
        argsValues = {}

        if not values or len(values) == 0:
            return argsValues

        for arg, pos in self.arg:
            argsValues[arg] = values[pos]

        return args_map

    def _map_values(self, args_map, values):
        values_map = {}
        for arg_name, pos in args_map.items():
            values_map[arg_name] = values[pos]
        return values_map

    def run(self):
        """
        Executes Conditions, Events, and Clauses in the Scenario for each set of Example values. 
        """

        runs = len(self.examples)
        if len(self.conditions) == 0:
            raise ValueError("No conditions specified for scenario {}".format(self.title))
             
        if len(self.events) == 0:
            raise ValueError("No events specified for scenario {}".format(self.title))
             
        if len(self.clauses) == 0:
            raise ValueError("No clauses specified for scenario {}".format(self.title))
                
        functions = []
        functions.extend(self.conditions)
        functions.extend(self.events)
        functions.extend(self.clauses)

        print("Executing scenario: '{}'".format(self.title))

	# examples has default value an empty tuple of values, so always there is at least one value
        runs = len(self.examples)
        for r in range(runs):
            try:
                values_map = self._map_values(self.args_map, self.examples[r])
                if values_map:
                    print("    With values: {}".format(values_map))

                closure = Scenario.Closure(values_map)

                for function in functions:
                    try:
                        function.enclose(closure)
                        print("    {}  {}".format(function.type(), function.signature()))
                        function.execute()
                    except Exception as ex:
                        raise Exception(" {} {} {}".format(function.type(), function.signature(), ex))

                print("    Success")

            except Exception as ex:
                print("    Failed: {}".format(ex))

    class Closure:
        """
        Contains a (possibly empty) set of values which are bound to the named arguments in a Function.
        Named arguments are strings with the format '<name>'.
        """
        def __init__(self, values_map):
            self.values_map = values_map

        def bind_arg(self, arg):
            # a unbound arg must be a string 
            if not isinstance(arg, str):
                return arg

            left = arg.find('<')
            right = arg.rfind('>')
            if left <0 or right < 0 or right <= left:
                 return arg
        
            arg_name = arg[left+1:right]
            try:
                return self.values_map[arg_name]
            except KeyError:
                raise ValueError("Argument {} not defined".format(arg))

        def bind_args(self, args, kwargs):
            
            if not self.values_map:
               return args, kwargs
    
            args_values = []
            for arg in args:
                args_values.append(self.bind_arg(arg))
            
            kwargs_values = {}
            for arg_name, arg_value in kwargs.items():
                kwargs_values[arg_name] = self.bind_arg(arg_value)
            
            return args_values, kwargs_values
    

    class Function:
        """
        Represents a Callable and its arguments, enclosed in a Closure.

        When the Function is executed, its named arguments are bound to the values
        in its Closure.
        """

        def __init__(self, func, args, kwargs):
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.closure = Scenario.Closure({})

        def enclose(self, closure):
            self.closure = closure

        def execute(self):
            args_values, kwargs_values = self.closure.bind_args(self.args, self.kwargs) 
            return self.func(*args_values, **kwargs_values)
     
        def signature(self):
            signature = "{}(".format(self.func.__name__)
            if self.args:
                signature = signature + (",".join(["%s"]*len(self.args)) % self.args)
            
            if self.kwargs:
                signature = signature + ','.join('{}={}'.format(k,v) for k,v in self.kwargs.items())
                
            signature = signature+")"

            return signature 


    class Condition(Function):
        """
        A Function that defines a condition that is satisfied by a Scenario.
        """
     
        @staticmethod
        def type():
            return "Condition"

        def __init__(self, func, args, kwargs):
            super().__init__(func, args, kwargs)

        def execute(self):
            super().execute()


    class Event(Function):
        """
        A Function that defines an Event that occurs in a Scenario
        """

        @staticmethod
        def type():
            return "Event"

        def __init__(self, func, args, kwargs):
            super().__init__(func, args, kwargs)

        
    class Clause(Function):
        """
        A Function that defines an Assertion that must be satisfied in the Scenario after
        the Events had occurred. 
        """

        @staticmethod
        def type():
            return "Clause"

        def __init__(self, func, args, kwargs, assertion, value):
            super().__init__(func, args, kwargs)
            self.assertion = assertion
            self.value = value
             
        def execute(self):
            result = super().execute()

            assertion_value = self.closure.bind_arg(self.value)
            if not self.assertion(result, assertion_value):
                raise Exception("Result '{}' does not satisfy assertion {} '{}'".format(result, self.assertion.__name__, assertion_value))

        def signature(self):
            sig = super().signature()
            return "{}.{}({})".format(sig, self.assertion.__name__, self.closure.bind_arg(self.value))
