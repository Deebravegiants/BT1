# [H] Vyper vulnerable to integer overflow in loop

## Summary
Severity: High
Advisory: GHSA-6r8q-pfpv-7cgj
CVE: CVE-2023-32058
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-6r8q-pfpv-7cgj
Type: github-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.8

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

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-6r8q-pfpv-7cgj
- https://nvd.nist.gov/vuln/detail/CVE-2023-32058
- https://github.com/vyperlang/vyper/commit/3de1415ee77a9244eb04bdb695e249d3ec9ed868
- https://github.com/pypa/advisory-database/tree/main/vulns/vyper/PYSEC-2023-78.yaml
- https://github.com/vyperlang/vyper
