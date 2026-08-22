# [M] multiple evaluation of contract address in call

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2022-29255
Published: 2022-06-06
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-4v9q-cgpw-cf38
Type: github-advisory

## Details
### Impact
when a calling an external contract with no return value, the contract address could be evaluated twice. this is usually only an efficiency problem, but if evaluation of the contract address has side effects, it could result in double evaluation of the side effects.

in the following example, `Foo(msg.sender).bar()` is the contract address for the following call (to `.foo()`), and could get evaluated twice

```vyper
interface Foo:
    def foo(): nonpayable
    def bar() -> address: nonpayable

@external
def do_stuff():
    Foo(Foo(msg.sender).bar()).foo()
```

### Patches
6b4d8ff185de071252feaa1c319712b2d6577f8d

### Workarounds
assign contract addresses to variables. the above example would change to
```vyper
@external
def do_stuff():
    t: Foo = Foo(msg.sender).bar()
    t.foo()
```

### References

### For more information
