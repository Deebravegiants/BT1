# [M] incorrect order of evaluation of side effects for some builtins

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2023-41052
CWE: Always-Incorrect Control Flow Implementation
Published: 2023-09-04
Source: https://github.com/advisories/GHSA-4hg4-9mf5-wxxq
Type: github-advisory

## Details
### Impact
The order of evaluation of the arguments of the builtin functions `uint256_addmod`, `uint256_mulmod`, `ecadd` and `ecmul` does not follow source order.
• For `uint256_addmod(a,b,c)` and `uint256_mulmod(a,b,c)`, the order is `c,a,b`.
• For `ecadd(a,b)` and `ecmul(a,b)`, the order is `b,a`.

Note that this behaviour is problematic when the evaluation of one of the arguments produces side effects that other arguments depend on. 

### Patches
https://github.com/vyperlang/vyper/pull/3583

### Workarounds
When using builtins from the list above, make sure that the arguments of the expression do not produce side effects or, if one does, that no other argument is dependent on those side effects.

### References
_Are there any links users can visit to find out more?_
