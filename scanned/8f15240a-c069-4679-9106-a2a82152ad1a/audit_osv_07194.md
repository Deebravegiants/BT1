# [M] BIT-node-2026-58041

## Summary
Severity: Medium
Advisory: BIT-node-2026-58041
Aliases: BIT-node-min-2026-58041, CVE-2026-58041
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-node-2026-58041
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <26.5.1

## Details
A flaw in Node.js node:sqlite allows a stale StatementSyncIterator created through DatabaseSync#createTagStore() to continue executing a cached prepared statement after it has been reset and rebound with new parameters. SQLTagStore resets cached statements using sqlite3_reset() directly, bypassing the iterator invalidation mechanism introduced for StatementSync in recent releases

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://nodejs.org/en/blog/vulnerability/july-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-58041
