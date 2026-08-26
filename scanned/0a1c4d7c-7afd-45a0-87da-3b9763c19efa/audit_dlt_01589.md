# [?] [consensus] fix a race condition

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-10-03
Source: https://github.com/aptos-labs/aptos-core/commit/d4c5b9a792ff528c81aa3029934188b550da8621
Type: security-commit

## Details
[consensus] fix a race condition

There's a race condition where if the commit proof is forwarded, sync manager decides to sync but fails to retrieve block or something,
then a lower round commit proof can come and decides to pause pre_commit and sync but previous commit proof can resume the pre_commit to
go beyond the target version.
