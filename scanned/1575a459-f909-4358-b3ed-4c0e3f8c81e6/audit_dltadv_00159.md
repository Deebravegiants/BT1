# [H] PYSEC-2022-198

## Summary
Severity: High
Advisory: PYSEC-2022-198
Aliases: CVE-2022-24845, GHSA-j2x6-9323-fp7h
Package: vyper
Published: 2022-04-13
Source: https://osv.dev/vulnerability/PYSEC-2022-198
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <049dbdc647b2ce838fae7c188e6bb09cf16e470b, >=0 <0.3.2

## Details
Vyper is a pythonic Smart Contract Language for the ethereum virtual machine. In affected versions, the return of `<iface>.returns_int128()` is not validated to fall within the bounds of `int128`. This issue can result in a misinterpretation of the integer value and lead to incorrect behavior. As of v0.3.0, `<iface>.returns_int128()` is validated in simple expressions, but not complex expressions. Users are advised to upgrade. There is no known workaround for this issue.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-j2x6-9323-fp7h
- https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b
