# [?] Merge pull request from GHSA-ph9x-4vc9-m39g

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-05-11
Source: https://github.com/vyperlang/vyper/commit/c3e68c302aa6e1429946473769dd1232145822ac
Type: security-commit

## Details
Merge pull request from GHSA-ph9x-4vc9-m39g

the routine for aligning call-site posargs and kwargs in
`vyper.codegen.context.lookup_internal_function` was incorrect in cases
where the internal function had more than one default argument - it
consumed default args at the call site from the end instead of the
beginning of the defaults list. this commit fixes and adds some tests
for the alignment routine.
