# [H] PYSEC-2023-77

## Summary
Severity: High
Advisory: PYSEC-2023-77
Aliases: CVE-2023-31146, GHSA-3p37-3636-q8wv
Package: vyper
Published: 2023-05-11
Source: https://osv.dev/vulnerability/PYSEC-2023-77
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <4f8289a81206f767df1900ac48f485d90fc87edb, >=0 <0.3.8

## Details
Vyper is a Pythonic smart contract language for the Ethereum virtual machine. Prior to version 0.3.8, during codegen, the length word of a dynarray is written before the data, which can result in out-of-bounds array access in the case where the dynarray is on both the lhs and rhs of an assignment. The issue can cause data corruption across call frames. The expected behavior is to revert due to out-of-bounds array access. Version 0.3.8 contains a patch for this issue.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-3p37-3636-q8wv
- https://github.com/vyperlang/vyper/commit/4f8289a81206f767df1900ac48f485d90fc87edb
