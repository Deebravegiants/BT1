# [H] incorrect ordering of default arguments passed to internal calls

## Summary
Severity: High
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-32059
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-ph9x-4vc9-m39g
Type: github-advisory

## Details
### Impact

Internal calls to internal functions with more than 1 default argument are compiled incorrectly. Depending on the number of arguments
provided in the call, the defaults are added not right-to-left, but left-to-right. If the types are incompatible,
typechecking is bypassed. In the `bar()` function in the following code, `self.foo(13)` is compiled to
`self.foo(13,12)` instead of `self.foo(13,1337)`.

```vyper
@internal
def foo(a:uint256 = 12, b:uint256 = 1337):
    pass

@internal
def bar():
    self.foo(13)
```

note that at the time of publication, the ability to pass kwargs to internal functions is an undocumented feature that does not seem to be widely used.

### Patches
patched in c3e68c302aa6e1429946473769dd1232145822ac

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_
