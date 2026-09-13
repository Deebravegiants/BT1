# [M] _abi_decode input not validated in certain complex expressions

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-42460
Published: 2023-09-26
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-cx2q-hfxr-rj97
Type: github-advisory

## Details
### Impact
`_abi_decode()` does not validate input when it is nested in an expression. the following example gets correctly validated (bounds checked):
```vyper
x: int128 = _abi_decode(slice(msg.data, 4, 32), int128)
```

however, the following example is not bounds checked
```vyper
@external
def abi_decode(x: uint256) -> uint256:
    a: uint256 = convert(_abi_decode(slice(msg.data, 4, 32), (uint8)), uint256) + 1
    return a  # abi_decode(256) returns: 257
```

the issue can be triggered by constructing an example where the output of `_abi_decode` is not internally passed to `make_setter` (an internal codegen routine) or other input validating routine.

### Patches
https://github.com/vyperlang/vyper/pull/3626

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_
