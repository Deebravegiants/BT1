# [C] @payloadcms/drizzle has SQL Injection in JSON/RichText Queries on PostgreSQL/SQLite Adapters

## Summary
Severity: Critical
Advisory: GHSA-xx6w-jxg9-2wh8
CVE: CVE-2026-25544
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-xx6w-jxg9-2wh8
Type: github-advisory

## Affected
- npm: `@payloadcms/drizzle` — affected >=0 <3.73.0

## Details
### Impact

When querying JSON or richText fields, user input was directly embedded into SQL without escaping, enabling blind SQL Injection attacks. An unauthenticated attacker could extract sensitive data (emails, password reset tokens) and achieve full account takeover without password cracking.

**Users are affected if ALL of these are true:**

1. Payload version < v3.73.0
2. Using a Drizzle-based database adapter (`@payloadcms/drizzle` as dependency):
   - `@payloadcms/db-postgres`
   - `@payloadcms/db-vercel-postgres`
   - `@payloadcms/db-sqlite`
   - `@payloadcms/db-d1-sqlite`
3. At least one accessible collection that has a `type: 'json'` or `type: 'richText'` field where `access.read` returns anything other than `false` (`true` or `Where` constraint)

**Users are NOT affected if:**

- Using `@payloadcms/db-mongodb`
- No JSON or richText fields exist in any collection
- All JSON/richText fields have `access: { read: () => false }`

### Patches

Upgrade to Payload **v3.73.0** or later.

### Workarounds

If a project cannot upgrade immediately, add `access: { read: () => false }` to all JSON and richText fields as a temporary mitigation.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-xx6w-jxg9-2wh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25544
- https://github.com/payloadcms/payload
