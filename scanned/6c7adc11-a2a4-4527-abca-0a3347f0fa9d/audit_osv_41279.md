# [H] Mockoon: Unauthenticated admin API + wildcard CORS allows mock-state hijack and secret theft

## Summary
Severity: High
Advisory: CVE-2026-59148
Aliases: GHSA-rqx4-3f6q-3x2v
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59148
Type: osv

## Details
Mockoon provides way to design and run mock APIs. Prior to 9.7.0, Mockoon's admin API in commons-server/src/libs/server/admin-api.ts is mounted on the same Express listener as user-defined mock routes, enabled by default in shipped runtimes, serves Access-Control-Allow-Origin: * with write methods allowed, and has no authentication. Any unauthenticated caller who can reach the mock server port can read MOCKOON_* environment variables, write arbitrary process environment variables through /mockoon-admin/env-vars, rewrite mock route bodies, statuses, and headers through PUT /mockoon-admin/environment, read transaction logs and SSE streams, and purge state. This issue is fixed in version 9.7.0.

## References
- https://github.com/mockoon/mockoon/releases/tag/v9.7.0
- https://mockoon.com/releases/9.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59148.json
- https://github.com/mockoon/mockoon/security/advisories/GHSA-rqx4-3f6q-3x2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-59148
- https://github.com/mockoon/mockoon/commit/c420b5a56918475b8663977b51e5f986e45b3299
- https://github.com/mockoon/mockoon/pull/2254
