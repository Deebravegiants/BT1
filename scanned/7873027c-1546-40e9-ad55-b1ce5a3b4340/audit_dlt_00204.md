# [M] Vyper's nonpayable default functions are sometimes payable

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2023-32675
CWE: Always-Incorrect Control Flow Implementation
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-vxmm-cwh2-q762
Type: github-advisory

## Details
### Impact
in contracts with at least one regular nonpayable function, due to the callvalue check being inside of the selector section, it is possible to send funds to the default function by using less than 4 bytes of calldata, even if the default function is marked `nonpayable`. this applies to contracts compiled with vyper<=0.3.7.
```vyper
# @version 0.3.7

# implicitly nonpayable
@external
def foo() -> uint256:
    return 1

# implicitly nonpayable
@external
def __default__():
    # could receive ether here
    pass
```

### Patches
this was fixed by the removal of the global calldatasize check in https://github.com/vyperlang/vyper/commit/02339dfda0f3caabad142060d511d10bfe93c520.

### Workarounds
don't use nonpayable default functions
