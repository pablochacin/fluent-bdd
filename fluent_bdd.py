import bdd

class BackgroundBuilder:

    class ConditionBuilder:

        def __init__(self, background, featureBld):
            self.background = background
            self.featureBld = featureBld

        def And(self, condition, *args, **kwargs):
            self.background.addCondition(condition, *args, **kwargs)
            return self

        def Scenario(self, title):
            return self.featureBld.Scenario(title)

     
    def __init__(self, featureBld, background):
        self.featureBld = featureBld
        self.background = background

    def Given(self, condition, *args, **kwargs):
        self.background.addCondition(condition, *args, **kwargs)
        return BackgroundBuilder.ConditionBuilder(self.background, self.featureBld)

class ScenarioBuilder:

    class ConditionBuilder:

        def __init__(self, scenarioBld):
           self.scenarioBld = scenarioBld

        def And(self, condition, *args, **kwargs):
            self.scenarioBld.scenario.addCondition(condition, *args, **kwargs)
            return self

        def When(self, event, *args, **kwargs):
            self.scenarioBld.scenario.addEvent(event, *args, **kwargs)
            return ScenarioBuilder.EventBuilder(self.scenarioBld)


    class EventBuilder:

        def __init__(self, scenarioBld):
           self.scenarioBld = scenarioBld

        def And(self, event, *args, **kwargs):
            self.scenarioStm.scenario.addEvent(event, *args, **kwargs)
            return self

        def Then(self, clause, *args, **kwargs):
            return ScenarioBuilder.AssertionBuilder(self.scenarioBld, clause, *args, **kwargs)

    class AssertionBuilder:

        def __init__(self, scenarioBld, clause, *args, **kwargs):
            self.scenarioBld = scenarioBld
            self.clause = clause
            self.args = args
            self.kwargs = kwargs

        def Is(self, value):
            self.scenarioBld.scenario.addClause(self.clause, bdd.Assertion.Is, value, *self.args, **self.kwargs)
            return ScenarioBuilder.ClauseBuilder(self.scenarioBld)

        def IsNot(self, value):
            self.scenarioBld.scenario.addClause(self.clause, bdd.Assertion.IsNot, value, *self.args, **self.kwargs)
            return ScenarioBuilder.ClauseBuilder(self.scenarioBld)

    class ClauseBuilder:

        def __init__(self, scenarioBld):
           self.scenarioBld = scenarioBld

        def And(self, clause, *args, **kwargs):
            return Scenariostatement.AssertionBuilder(self.scenarioBld, clause, *args, **kwargs)

        def Scenario(self, title):
            return self.scenarioBld.featureBld.Scenario(title)

        def Examples(self, arg_names, examples):
            self.scenarioBld.scenario.setExamples(arg_names, examples)
            return self 

        def Test(self):
            return self.scenarioBld.featureBld.Test()

    def __init__(self, featureBld, scenario):
        self.featureBld = featureBld
        self.scenario = scenario

    def Given(self, condition, *args, **kwargs):
        self.scenario.addCondition(condition, *args, **kwargs)
        return ScenarioBuilder.ConditionBuilder(self)

    def When(self, event, *args, **kwargs):
        self.scenario.addEvent(event, *args, **kwargs)
        return ScenarioBuilder.EventBuilder(self)


class FeatureBuilder:

    def __init__(self, name):
        self.feature= bdd.Feature(name)

    def __enter__(self):
        return self

    def __exit__(self,*args):
        return self.feature.test()

    def Background(self):
        b = bdd.Feature.Background()
        self.feature.setBackground(b)
        return BackgroundBuilder(self,b)

    def Scenario(self, title):
        s = self.feature.addScenario(title)
        return ScenarioBuilder(self, s)

    def Test(self):
        return self.feature.test()
