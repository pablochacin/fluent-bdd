from bdd import Scenario

def echo(a):
    return a

class SUT:

    def f0(self):
        print("Executing f0()")

    def f1(self, a):
        print("Executing f1({})".format(a))

    def f2(self, a, b):
        print("Executing f2({},{})".format(a, b))

    def fkw(self, a=None, b=None, c=None):
        print("Executing fkw(a={}, b={}, c={})".format(a, b, c))

    def fail(self):
        print("Executing fail()")
        raise Exception("Fail!")

def main():

    sut = SUT()

    Scenario("Success Test").Given(sut.f0).When(sut.f2, 1, 2).Then(echo, True).Is(True).Run()
    Scenario("No Conditions").When(sut.f2, 1, 2).Then(echo, True).Is(True).Run()
    Scenario("Multiple Conditions").Given(sut.f0).And(sut.f1,'a').When(sut.f2, 1, 2).Then(echo, True).Is(True).Run()
    Scenario("Kwargs").When(sut.fkw, a=1, b=2, c=3).Then(echo, True).Is(True).Run()
    Scenario("Invalid Kwargs").When(sut.fkw, a=1, b=2, d=3).Then(echo, True).Is(True).Run()
    Scenario("Failing Assertion").Given(sut.f0).When(sut.f2, 1, 2).Then(echo, True).IsNot(True).Run()
    Scenario("Failing condition").Given(sut.f0).When(sut.fail).Then(echo, True).Is(True).Run()
    Scenario("Wrong function arity").Given(sut.f0).When(sut.f1,1,2).Then(echo, True).Is(True).Run()

if __name__ == "__main__":
    main()
