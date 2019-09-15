# Fluent BDD

Fluent BDD is a minimalistic testing framework with a fluent API.

A Feauture is tested by means of a series of Scenarios.

A Scenario is defined as a sequence of Conditions, followed by
a series of Events and the Clauses that must be satiesfied at
the end. Multiple Conditions, Events and Clauses can be specified.

## Fluent API

The API for defining a test scenario follows a fluent style.
Function calls can be chanined in a close-to-english syntax.

Example:
```
Feature("My feature") \
    .Scenario("Multiple conditions")        \
        .Given(f1, 1, 'B').And(f1, 1, 'A') \
        .When(f2, a=3, b=1)                \
        .Then(f3).Is(True)                 \
    .Test()
```

## Function invocation

Actions, Events and Clauses receive a function as first parameter,
followed by a (potentially empty) sequence of arguments, and
an optional series of named arguments.

The functions used in the statements can be static methods or instance method.

Example:

    ```
    class SUT:
        
    def f(self):
            return
    
    def v(self):
        return True

    def verify(sut):
        return sut.v()

    s = SUT()
    Scenario("Class methods").when(s.f).then(verify,s).Is(True).Run()
    ```

## Clauses and assertions

Clauses are defined as a invocation of a function followed by an assertion on the returning value.
Supported assertions are:
* Is(value)
* IsNot(value)

## Background

In some cases, multiple scenarios share the same Conditions. In that case,
it is possible to define a Background with the common conditions, which are
copied to all Scenarios in the Feature.


Example:
```
Feature("With Background") \ 
    .Background()       \
         .Given(f,a, b)    \
         .Given(g,1)       \
    .Scenario("Test 1")            \
        .When(f1,'c')             \
        .Then(f2).Is(True)        \
    .Scenario("Test 2")            \
        .When(f,'a')              \
        .Then(f2).Is(False)       \
    .Test()
    ```
## Using examples

Sometimes is convenient to execute the same test Scenario with multiple arguments for
the different statements. The `Examples` function allows setting a list of named
parameters which can be used in any statement. Named arguments are references using
its name enclosed in '{}'.

Example:
```
    Feature("Scenario With examples") \
        .Scenario("With Examples") \
            .AsVerbose()
            .Given(sut.f0)                  \
            .When(sut.f2, '<a>', 'b')       \
            .Then(echo, '<c>').Is('<d>')    \
            .Examples(('a', 'b','c','d'), \
                 [(1,2,True,True),          \
                  (2,3,True,False)])        \
         .Test()

        Executing 'With Examples' with values {'a': 1, 'b': 2, 'c': True, 'd': True}
          Executing condition f0()
          Executing event f2(1,b)
          Executing clause echo(True)
        Scenario 'With Examples' success

        Executing 'With Examples' with values {'a': 2, 'b': 3, 'c': True, 'd': False}
          Executing condition f0()
          Executing event f2(2,b)
          Executing clause echo(True)
        Scenario 'With Examples' failed: Clause echo(True) failed with error: assertion Is(True,False) failed
 ```
   Notice the function `f2` is called with the literal `b` as second argument while
   the first argument `<a>` is replaced on each execution with the correspoding
   value.


## Feature as a context manager

Feature class implements the Context Manager interface and can be used in `with` statements for improved legibility when chaining multiple scenarios. The `Test` method is invoked automatically when closing the `with` statement. 

```
with Feature("With Background") as f:
    f.Background()       \
         .Given(f,a, b)    \
         .Given(g,1)       

    f.Scenario("Test 1")            \
        .When(f1,'c')             \
        .Then(f2).Is(True)        

    f.Scenario("Test 2")            \
        .When(f,'a')              \
        .Then(f2).Is(False)
```


(c) 2019 Pablo Chacin
