# [?] Merge pull request from GHSA-6r8q-pfpv-7cgj

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/commit/3de1415ee77a9244eb04bdb695e249d3ec9ed868
Type: security-commit

## Details
Merge pull request from GHSA-6r8q-pfpv-7cgj

for loops of the form `for i in range(x, x+N)`, the range of the
iterator is not checked, leading to potential overflow. the following
example demonstrates the potential for overflow:

```
@external
def test() -> uint16:
    x:uint8 = 255
    a:uint8 = 0
    for i in range(x, x+2):
        a = i
    return convert(a,uint16)  # returns 256
```

this commit fixes the issue by adding a range check before entering the
loop body.
