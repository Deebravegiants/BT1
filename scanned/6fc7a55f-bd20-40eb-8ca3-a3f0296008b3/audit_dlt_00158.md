# [H] OOB DynArray access when array is on both LHS and RHS of an assignment

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-31146
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-3p37-3636-q8wv
Type: github-advisory

## Details
### Impact
during codegen, the length word of a dynarray is written before the data, which can result in OOB array access in the case where the dynarray is on both the lhs and rhs of an assignment. here is a minimal example producing the issue:
```vyper
a:DynArray[uint256,3]
@external
def test() -> DynArray[uint256,3]:
    self.a = [1,2,3]
    self.a = empty(DynArray[uint256,3])
    self.a = [self.a[0],self.a[1],self.a[2]]
    return self.a # return [1,2,3]
```

and here is an example demonstrating the issue can cause data corruption across call frames:

```vyper
@external
def test() -> DynArray[uint256,3]:
    self.a()
    return self.b() # return [1,2,3]

@internal
def a():
    a: uint256 = 0    
    b: uint256 = 1    
    c: uint256 = 2    
    d: uint256 = 3

@internal
def b() -> DynArray[uint256,3]:
    a: DynArray[uint256,3] = empty(DynArray[uint256,3])
    a = [a[0],a[1],a[2]]
    return a
```

examples involving append and pop:
```vyper
@internal
def foo():
```

_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/security/advisories/GHSA-3p37-3636-q8wv_
