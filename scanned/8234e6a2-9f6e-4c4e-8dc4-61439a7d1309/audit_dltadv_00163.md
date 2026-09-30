# [H] PYSEC-2023-79

## Summary
Severity: High
Advisory: PYSEC-2023-79
Aliases: CVE-2023-32059, GHSA-ph9x-4vc9-m39g
Package: vyper
Published: 2023-05-11
Source: https://osv.dev/vulnerability/PYSEC-2023-79
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <c3e68c302aa6e1429946473769dd1232145822ac, >=0 <0.3.8

## Details
Vyper is a Pythonic smart contract language for the Ethereum virtual machine. Prior to version 0.3.8, internal calls with default arguments are compiled incorrectly. Depending on the number of arguments provided in the call, the defaults are added not right-to-left, but left-to-right. If the types are incompatible, typechecking is bypassed. The ability to pass kwargs to internal functions is an undocumented feature that is not well known about. The issue is patched in version 0.3.8.

## References
- https://github.com/vyperlang/vyper/commit/c3e68c302aa6e1429946473769dd1232145822ac
- https://github.com/vyperlang/vyper/security/advisories/GHSA-ph9x-4vc9-m39g
