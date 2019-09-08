from fluent_bdd import FeatureBuilder

def echo(a):
    return a

class SUT:

    def f0(self):
        pass

    def f1(self, a):
        pass

    def f2(self, a, b):
        pass

    def fkw(self, a=None, b=None, c=None):
        pass

    def fail(self):
        raise Exception("Fail!")

def main():

    sut = SUT()

    with FeatureBuilder("My feature") as f:        
        f.Scenario("Success Test") \
            .Given(sut.f0).When(sut.f2, 1, 2) \
            .Then(echo, True).Is(True) 

        f.Scenario("With Examples") \
            .Examples(('a', 'b','c'), [(1,2,True), (2,3,False)]) \
            .Given(sut.f0) \
            .When(sut.f2, 'a', '{b}')  \
            .Then(echo, True).Is('{c}') \

        f.Scenario("No Conditions") \
            .When(sut.f2, 1, 2) \
            .Then(echo, True).Is(True) 

        f.Scenario("Multiple Conditions") \
            .Given(sut.f0) \
            .And(sut.f1,'a') \
            .When(sut.f2, 1, 2) \
            .Then(echo, True).Is(True) 

        f.Scenario("Kwargs") \
            .When(sut.fkw, a=1, b=2, c=3) \
            .Then(echo, True).Is(True) 

        f.Scenario("Invalid Kwargs") \
            .When(sut.fkw, a=1, b=2, d=3) \
            .Then(echo, True).Is(True) 

        f.Scenario("Failing Assertion") \
            .Given(sut.f0).When(sut.f2, 1, 2) \
            .Then(echo, False).Is(True) \

        f.Scenario("Failing condition") \
            .Given(sut.f0) \
            .When(sut.fail) \
            .Then(echo, True).Is(True) 

        f.Scenario("Wrong function arity") \
            .Given(sut.f0) \
            .When(sut.f1,1,2) \
            .Then(echo, True).Is(True) 

    FeatureBuilder("My feature with background") \
            .Background().Given(sut.f0).And(sut.f2,'a','b') \
            .Scenario("With Background") \
                .When(sut.f2, 1, 2) \
                .Then(echo, True).Is(True) \
            .Test()

if __name__ == "__main__":
    main()
