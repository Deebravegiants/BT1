# [M] Cross-Shard Failovers May Lead to Partial Transaction Commit in MongoDB Server

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-14345
Aliases: CVE-2025-14345
Ecosystem: Bitnami
Published: 2026-05-13
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-14345
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.1

## Details
A post-authentication flaw in the network two-phase commit protocol used for cross-shard transactions in MongoDB Server may lead to logical data inconsistencies under specific conditions which are not predictable and exist for a very short period of time. This error can cause the transaction coordination logic to misinterpret the transaction as committed, resulting in inconsistent state on those shards. This may lead to low integrity and availability impact.

This issue impacts MongoDB Server v8.0 versions prior to 8.0.16, MongoDB Server v7.0 versions prior to 7.0.26 and MongoDB server v8.2 versions prior to 8.2.2.

## References
- https://jira.mongodb.org/browse/SERVER-106075
- https://nvd.nist.gov/vuln/detail/CVE-2025-14345
