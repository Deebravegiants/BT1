# [M] PYSEC-2021-366

## Summary
Severity: Medium
Advisory: PYSEC-2021-366
Aliases: CVE-2021-41122, GHSA-c7pr-343r-5c46
Package: vyper
Published: 2021-10-05
Source: https://osv.dev/vulnerability/PYSEC-2021-366
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.0

## Details
Vyper is a Pythonic Smart Contract Language for the EVM. In affected versions external functions did not properly validate the bounds of decimal arguments. The can lead to logic errors. This issue has been resolved in version 0.3.0.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-c7pr-343r-5c46
- https://github.com/vyperlang/vyper/pull/2447
