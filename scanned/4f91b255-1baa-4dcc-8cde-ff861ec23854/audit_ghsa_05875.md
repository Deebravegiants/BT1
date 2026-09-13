# [M] New API: Redis user quota cache overwrite via PUT /api/user/self allows quota bypass

## Summary
Severity: Medium
Advisory: GHSA-j6gc-4893-qwmp
CVE: CVE-2026-64865
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-j6gc-4893-qwmp
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <1.0.0-rc.16

## Details
### Summary
Authenticated users can repeatedly call PUT /api/user/self with language or sidebar_modules while relay requests are consuming quota. The settings path reads a full User snapshot and writes it back through User.Update(), which refreshes Redis with RedisHSetObj and overwrites the Quota field. This can erase concurrent HINCRBY quota deductions and keep cached balance artificially high, allowing calls far beyond the paid quota.

### Impact
A low-privileged authenticated user may bypass quota enforcement and cause financial loss to operators. Authentication and pre-consumption use cached quota, while DB/log usage can continue increasing.

### Affected Components
- controller/user.go: UpdateSelf language/sidebar_modules branches
- model/user.go: User.Update / UpdateWithTx full snapshot update
- model/user_cache.go: updateUserCache RedisHSetObj full hash write
- model/user.go: GetUserQuota reads Redis cache first

### Root Cause
Normal billing uses Redis HINCRBY on user:<id>.Quota, while settings updates use a stale full user snapshot to HSET the entire cache hash, including Quota. These two writers race on the same Redis field.

### Patches
This issue is fixed in v1.0.0-rc.16. The fix makes user setting updates field-scoped, prevents stale user snapshots from overwriting accounting fields, and keeps generic user cache refreshes from modifying Quota. Quota cache updates are reserved for atomic quota delta paths or explicit quota synchronization paths.

### Workarounds
If upgrading immediately is not possible, operators should temporarily restrict or rate-limit PUT /api/user/self and avoid allowing frequent user setting updates while Redis-backed quota cache is enabled. This is only a mitigation; upgrading is recommended.

### Remediation
Upgrade to v1.0.0-rc.16 or later. Deployments with Redis enabled should restart application instances after upgrading so stale in-process code paths are removed.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-j6gc-4893-qwmp
- https://github.com/QuantumNous/new-api/commit/dfc0d6324b40c1d6c2972e524409f933541bfb0f
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.16
