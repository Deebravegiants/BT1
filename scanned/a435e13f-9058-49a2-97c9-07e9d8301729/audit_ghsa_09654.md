# [H] Drizzle ORM has SQL injection via improperly escaped SQL identifiers

## Summary
Severity: High
Advisory: GHSA-gpj5-g38j-94v9
CVE: CVE-2026-39356
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-gpj5-g38j-94v9
Type: github-advisory

## Affected
- npm: `drizzle-orm` — affected >=0 <0.45.2
- npm: `drizzle-orm` — affected >=1.0.0-beta.2 <1.0.0-beta.20

## Details
### Summary

Drizzle ORM improperly escaped quoted SQL identifiers in its dialect-specific `escapeName()` implementations. In affected versions, embedded identifier delimiters were not escaped before the identifier was wrapped in quotes or backticks.

As a result, applications that pass attacker-controlled input to APIs that construct SQL identifiers or aliases, such as `sql.identifier()`, `.as()`, may allow an attacker to terminate the quoted identifier and inject SQL.

### Affected components

The issue affects the identifier escaping logic used by the PostgreSQL, MySQL, SQLite, SingleStore, and Gel dialects.

### Impact

This issue only affects applications that pass untrusted runtime input into identifier or alias construction. Common examples include dynamic sorting, dynamic report builders, and CTE or alias names derived from request parameters.

Depending on the database dialect, query context, and database permissions, successful exploitation may enable blind or direct data disclosure, schema enumeration, query manipulation, privilege escalation, or destructive operations.

Applications that use only static schema objects, or that strictly map user input through an allowlist of known column or alias names, are not affected.

### Details

In affected versions, `escapeName()` wrapped the identifier but did not escape the quote delimiter inside the identifier value:

- PostgreSQL / SQLite / Gel: `"` was not doubled to `""`
- MySQL / SingleStore: `` ` `` was not doubled to `` `` ``

Because of this, crafted input containing the dialect-specific identifier delimiter could break out of the quoted identifier and be interpreted as SQL syntax.

A representative vulnerable pattern is dynamic sorting using untrusted input:

```ts
const sortField = req.query.sort || 'id';

const rows = await db
  .select()
  .from(users)
  .orderBy(sql.identifier(sortField));

## References
- https://github.com/drizzle-team/drizzle-orm/security/advisories/GHSA-gpj5-g38j-94v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39356
- https://github.com/drizzle-team/drizzle-orm
