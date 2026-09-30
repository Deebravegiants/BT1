# [H] PYSEC-2021-365

## Summary
Severity: High
Advisory: PYSEC-2021-365
Aliases: CVE-2021-41121, GHSA-xv8x-pr4h-73jv
Package: vyper
Published: 2021-10-06
Source: https://osv.dev/vulnerability/PYSEC-2021-365
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0.3.0

## Details
Vyper is a Pythonic Smart Contract Language for the EVM. In affected versions when performing a function call inside a literal struct, there is a memory corruption issue that occurs because of an incorrect pointer to the the top of the stack. This issue has been resolved in version 0.3.0.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-xv8x-pr4h-73jv
- https://github.com/vyperlang/vyper/pull/2447
