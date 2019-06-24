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

    class Event:

        def __init__(self, scenario):
           self.scenario = scenario

        def And(self, event, *args, **kwargs):
            self.scenario.add_event(event, args, kwargs)
            return Scenario.Event(self.scenario)

        def Then(self, clause, *args, **kwargs):
            return Scenario.OpenClause(self.scenario, clause, args, kwargs)

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

        def Run(self):
            self.scenario.Run()


    class Assertion:

        @staticmethod
        def Is(expected, actual):
            return expected == actual

        @staticmethod
        def IsNot(expected, actual):
            return expected != actual


    def __init__(self, title):
        self.title = title
        self.conditions = []
        self.events = []
        self.clauses = []

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

    def Run(self):

        try:
            
            if len(self.events) == 0:
                raise ValueError("No events specified for scenario {}".format(self.title))
            
            if len(self.clauses) == 0:
                raise ValueError("No clauses specified for scenario {}".format(self.title))
            
            for condition, args, kwargs in self.conditions:
                condition_str = self._function_signature(condition, *args, **kwargs)
                try:
                    condition(*args, **kwargs)
                except Exception as ex:
                    raise Exception("Condition {} Failed with error: {}".format(condition_str, ex))

            for event, args, kwargs in self.events:
                event_str = self._function_signature(event, *args, **kwargs)
                try:
                    event(*args, **kwargs)
                except Exception as ex:
                    raise Exception("Event {} Failed with error: {}".format(event_str, ex))

            for clause, args, kwargs, assertion, value in self.clauses:
                clause_str = self._function_signature(clause, *args, **kwargs)
                result = None
                try:
                    result = clause(*args, **kwargs)
                except Exception as ex:
                     raise Exception("Clause {} Failed with error: {}".format(clause_str, ex))

                if not assertion(result, value):
                    raise Exception("Clause {} {} '{}' Actual '{}' ".format(clause_str, assertion.__name__, value, result))

            print("Scenario {} success".format(self.title))

        except Exception as ex:
            print("Scenario {} failed: {}".format(self.title, ex.message))

    def _function_signature(self, function, *args, **kwargs):
        signature = "{}(".format(function.__name__)
        if args:
            signature = signature + (",".join(["%s"]*len(args)) % args)
        
        if kwargs:
            signature = signature + ','.join('{}={}'.format(k,v) for k,v in kwargs.items())
            
        signature = signature+")"

        return signature

         
