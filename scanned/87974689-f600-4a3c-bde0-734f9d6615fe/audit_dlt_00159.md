# [M] Integer overflow for loops of form `for i in range(x, x+N)`

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-32058
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-6r8q-pfpv-7cgj
Type: github-advisory

## Details
### Impact

Due to missing overflow check for loop variables, by assigning the iterator of a loop to a variable, it is possible to overflow the type of the latter.

In the following example, calling `test` returns `354`, meaning that the variable `a` did store `354` a value out of bound for the type `uint8`.

```Vyper
@external
def test() -> uint16:
    x:uint8 = 255
    a:uint8 = 0
    for i in range(x, x+100):
        a = i
    return convert(a,uint16)
```

The issue seems to happen only in loops of type `for i in range(a, a + N)` as in loops of type `for i in range(start, stop)` and `for i in range(stop)`, the compiler is able to raise a `TypeMismatch` when trying to overflow the variable.

thanks to @trocher for reporting

### Patches

patched in 3de1415ee77a9244eb04bdb695e249d3ec9ed868

### Workarounds
