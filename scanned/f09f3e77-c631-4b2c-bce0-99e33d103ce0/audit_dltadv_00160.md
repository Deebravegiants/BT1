# [H] PYSEC-2023-76

## Summary
Severity: High
Advisory: PYSEC-2023-76
Aliases: CVE-2023-30837, GHSA-mgv8-gggw-mrg6
Package: vyper
Published: 2023-05-08
Source: https://osv.dev/vulnerability/PYSEC-2023-76
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <0bb7203b584e771b23536ba065a6efda457161bb, >=0 <0.3.8

## Details
Vyper is a pythonic smart contract language for the EVM. The storage allocator does not guard against allocation overflows in versions prior to 0.3.8. An attacker can overwrite the owner variable. This issue was fixed in version 0.3.8.

## References
- https://github.com/vyperlang/vyper/commit/0bb7203b584e771b23536ba065a6efda457161bb
- https://github.com/vyperlang/vyper/security/advisories/GHSA-mgv8-gggw-mrg6
