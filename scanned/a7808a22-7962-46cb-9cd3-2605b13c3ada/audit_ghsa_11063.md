# [H] Parse Server has SQL Injection through aggregate and distinct field names in PostgreSQL adapter

## Summary
Severity: High
Advisory: GHSA-p2w6-rmh7-w8q3
CVE: CVE-2026-33539
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-p2w6-rmh7-w8q3
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.53
- npm: `parse-server` — affected >=0 <8.6.59

## Details
### Impact

An attacker with master key access can execute arbitrary SQL statements on the PostgreSQL database by injecting SQL metacharacters into field name parameters of the aggregate `$group` pipeline stage or the `distinct` operation. This allows privilege escalation from Parse Server application-level administrator to PostgreSQL database-level access.

Only Parse Server deployments using PostgreSQL are affected. MongoDB deployments are not affected.

### Patches

Field names in the aggregate `$group._id` object values and `distinct` dot-notation parameters are now validated to only contain alphanumeric characters and underscores, preventing SQL injection via the `:raw` interpolation used in the PostgreSQL storage adapter.

### Workarounds

No workaround. Upgrade to a patched version.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-p2w6-rmh7-w8q3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33539
- https://github.com/parse-community/parse-server/pull/10272
- https://github.com/parse-community/parse-server/pull/10273
- https://github.com/parse-community/parse-server/commit/03249f9bf5b8783c8b848f84dab791ff0b761b8c
- https://github.com/parse-community/parse-server/commit/bdddab5f8b61a40cb8fc62dd895887bdd2f3838e
- https://github.com/parse-community/parse-server
