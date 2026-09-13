# [M] vyper default functions don't respect nonreentrancy keys

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2024-32648
CWE: Improper Locking
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-m2v9-w374-5hj9
Type: github-advisory

## Details
### Summary
Prior to v0.3.0, `__default__()` functions did not respect the `@nonreentrancy` decorator and the lock was not emitted. This is a known bug and was already visible in the issue tracker (https://github.com/vyperlang/vyper/issues/2455), but it is being re-issued as an advisory so that tools relying on the advisory publication list can incorporate it into their searches.

A contract search was additionally performed and no vulnerable contracts were found in production.

### PoC
```vyper
@external
@payable
@nonreentrant("default")
def __default__():
    pass
```

after codegen:
```
[seq,
  [if, [lt, calldatasize, 4], [goto, fallback]],
  [mstore, 28, [calldataload, 0]],
  [with, _func_sig, [mload, 0], seq],
  [seq_unchecked,
    [label, fallback],
    [seq,
      pass,
      # Line 5
      pass,
      pass,
      # Line 4
      stop]]],
```

### Impact
No vulnerable production contracts were found. Additionally, using a lock on a `default` function is a very sparsely used pattern. As such, the impact is `low`.
