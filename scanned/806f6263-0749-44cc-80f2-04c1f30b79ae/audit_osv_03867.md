# [M] ALPINE-CVE-2026-58041

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-58041
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-58041
Type: osv

## Affected
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js node:sqlite allows a stale StatementSyncIterator created through DatabaseSync#createTagStore() to continue executing a cached prepared statement after it has been reset and rebound with new parameters. SQLTagStore resets cached statements using sqlite3_reset() directly, bypassing the iterator invalidation mechanism introduced for StatementSync in recent releases

This vulnerability affects Node.js **22.x**, **24.x**, and **26.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-58041
