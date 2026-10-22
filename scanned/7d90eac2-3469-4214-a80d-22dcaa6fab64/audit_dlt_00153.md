# [M] reversed order of side effects for some operations

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-40015
Published: 2023-09-02
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-g2xh-c426-v8mf
Type: github-advisory

## Details
### Impact

For the following (probably non-exhaustive) list of expressions, the compiler evaluates the arguments from right to left instead of left to right.

```
- unsafe_add
- unsafe_sub
- unsafe_mul
- unsafe_div
- pow_mod256
- |, &, ^ (bitwise operators)
- bitwise_or (deprecated)
- bitwise_and (deprecated)
- bitwise_xor (deprecated)
- raw_call
- <, >, <=, >=, ==, !=
- in, not in (when lhs and rhs are enums)
```

This behaviour becomes a problem when the evaluation of one of the arguments produces side effects that other arguments depend on. The following expressions can produce side-effect:

- state modifying external call 
- state modifying internal call
- `raw_call`
- `pop()` when used on a Dynamic Array stored in the storage
- `create_minimal_proxy_to`
- `create_copy_of`
- `create_from_blueprint`

For example:

```Vyper
f:uint256

@internal
def side_effect() -> uint256:
    self.f = 12
    return 1

@external
def foo() -> uint256:
    return unsafe_add(self.f,self.side_effect()) # returns 13 instead of 1
```

```Vyper
a:DynArray[uint256, 12]
@external
def bar() -> bool:
    self.a = [1,2,3]
    return len(self.a) == self.a.pop() # return false instead of true
```

### Patches
not yet patched, will address in a future release. tracking in https://github.com/vyperlang/vyper/issues/3604.

### Workarounds

When using expressions from the list above, make sure that the arguments of the expression do not produce side effects or, if one does, that no other argument is dependent on those side effects.

### References
_Are there any links users can visit to find out more?_
