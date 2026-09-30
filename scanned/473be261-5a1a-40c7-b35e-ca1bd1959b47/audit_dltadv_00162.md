# [H] PYSEC-2023-78

## Summary
Severity: High
Advisory: PYSEC-2023-78
Aliases: CVE-2023-32058, GHSA-6r8q-pfpv-7cgj
Package: vyper
Published: 2023-05-11
Source: https://osv.dev/vulnerability/PYSEC-2023-78
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <3de1415ee77a9244eb04bdb695e249d3ec9ed868, >=0 <0.3.8

## Details
Vyper is a Pythonic smart contract language for the Ethereum virtual machine. Prior to version 0.3.8, due to missing overflow check for loop variables, by assigning the iterator of a loop to a variable, it is possible to overflow the type of the latter. The issue seems to happen only in loops of type `for i in range(a, a + N)` as in loops of type `for i in range(start, stop)` and `for i in range(stop)`, the compiler is able to raise a `TypeMismatch` when trying to overflow the variable. The problem has been patched in version 0.3.8.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-6r8q-pfpv-7cgj
- https://github.com/vyperlang/vyper/commit/3de1415ee77a9244eb04bdb695e249d3ec9ed868
