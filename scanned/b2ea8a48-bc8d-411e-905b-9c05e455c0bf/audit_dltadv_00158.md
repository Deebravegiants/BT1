# [H] PYSEC-2022-197

## Summary
Severity: High
Advisory: PYSEC-2022-197
Aliases: CVE-2022-24788, GHSA-4mrx-6fxm-8jpg
Package: vyper
Published: 2022-04-13
Source: https://osv.dev/vulnerability/PYSEC-2022-197
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <049dbdc647b2ce838fae7c188e6bb09cf16e470b, >=0 <0.3.2

## Details
Vyper is a pythonic Smart Contract Language for the ethereum virtual machine. Versions of vyper prior to 0.3.2 suffer from a potential buffer overrun. Importing a function from a JSON interface which returns `bytes` generates bytecode which does not clamp bytes length, potentially resulting in a buffer overrun. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/vyperlang/vyper/commit/049dbdc647b2ce838fae7c188e6bb09cf16e470b
- https://github.com/vyperlang/vyper/security/advisories/GHSA-4mrx-6fxm-8jpg
