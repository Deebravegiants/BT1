# [M] vyper performs double eval of the slice start/length args in certain cases

## Summary
Severity: Medium
Chain: Vyper
Component: vyper
CVE: CVE-2024-32646
CWE: Improper Input Validation
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-r56x-j438-vw5m
Type: github-advisory

## Details
### Summary
Using the `slice` builtin can result in a double eval vulnerability when the buffer argument is either `msg.data`, `self.code` or `<address>.code` and either the `start` or `length` arguments have side-effects.

A contract search was performed and no vulnerable contracts were found in production. Having side-effects in the start and length patterns is also an unusual pattern which is not that likely to show up in user code. It is also much harder (but not impossible!) to trigger the bug since `0.3.4` since the unique symbol fence was introduced (https://github.com/vyperlang/vyper/pull/2914).

### Details
It can be seen that the `_build_adhoc_slice_node` function of the `slice` builtin doesn't cache the mentioned arguments to the stack: https://github.com/vyperlang/vyper/blob/4595938734d9988f8e46e8df38049ae0559abedb/vyper/builtins/functions.py#L244

As such, they can be evaluated multiple times (instead of retrieving the value from the stack).

### PoC
with Vyper version `0.3.3+commit.48e326f` the call to `foo` passes the `asserts`:
```vyper
l: DynArray[uint256, 10]

@external
def foo(cs: String[64]) -> uint256:
    for i in range(10):
        self.l.append(1)
    assert len(self.l) == 10
    s: Bytes[64] = b""
    s = slice(msg.data, self.l.pop(), 3)
    assert len(self.l) == 10 - 2
    return len(self.l)
```

### Patches
Patched in https://github.com/vyperlang/vyper/pull/3976.

### Impact
No vulnerable production contracts were found.
