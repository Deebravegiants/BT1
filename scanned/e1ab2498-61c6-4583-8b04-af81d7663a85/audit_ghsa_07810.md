# [M] payload-preferences has Cross-Collection IDOR in Access Control (Multi-Auth Environments)

## Summary
Severity: Medium
Advisory: GHSA-jq29-r496-r955
CVE: CVE-2026-25574
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-jq29-r496-r955
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.74.0

## Details
### Impact

A cross-collection Insecure Direct Object Reference (IDOR) vulnerability exists in the `payload-preferences` internal collection. In multi-auth collection environments using Postgres or SQLite with default serial/auto-increment IDs, authenticated users from one auth collection can read and delete preferences belonging to users in different auth collections when their numeric IDs collide.

**Users are affected if ALL of these are true:**

- Multiple auth collections configured (e.g., `admins` + `customers`)
- Postgres or SQLite database adapter with serial/auto-increment IDs
- Users in different auth collections with the same numeric ID

**Not affected:**

- `@payloadcms/db-mongodb` adapter
- Single auth collection environments
- Postgres/SQLite with `idType: 'uuid'`

### Patches

This vulnerability has been patched in **v3.74.0**. Users should upgrade to v3.74.0 or later.

### Workarounds

There is no workaround other than upgrading. Users with multiple auth collections using Postgres or SQLite with serial IDs should upgrade immediately.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-jq29-r496-r955
- https://nvd.nist.gov/vuln/detail/CVE-2026-25574
- https://github.com/payloadcms/payload
