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
```

_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/security/advisories/GHSA-g2xh-c426-v8mf_
