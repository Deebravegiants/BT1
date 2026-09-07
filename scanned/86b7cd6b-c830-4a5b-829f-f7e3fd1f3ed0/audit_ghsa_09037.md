# [H] MikroORM has SQL injection via runtime-controlled identifiers and JSON-path keys

## Summary
Severity: High
Advisory: GHSA-cfw5-68c4-ffqp
CVE: CVE-2026-44680
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-cfw5-68c4-ffqp
Type: github-advisory

## Affected
- npm: `@mikro-orm/sql` — affected >=0 <7.0.14
- npm: `@mikro-orm/knex` — affected >=0 <6.6.14

## Details
## Summary

MikroORM's identifier-quoting helper (`Platform.quoteIdentifier` and the postgres/mssql overrides) and its JSON-path emitters (`Platform.getSearchJsonPropertyKey`, `quoteJsonKey`) did not properly escape characters that delimit the SQL identifier or string-literal context they emit into. When application code passes attacker-influenced strings to public ORM APIs that expect an identifier or a JSON-property filter, an attacker can break out of the quoted context and inject arbitrary SQL.

## Affected APIs

The vulnerability is reachable when application code passes an attacker-influenced string to any of the following documented APIs:

* **Multi-tenant `schema` option** — `em.fork({ schema })`, `qb.withSchema(name)`, `wrap(entity).setSchema(name)`, `em.create(Cls, data, { schema })`. The schema name is concatenated into the SQL identifier and never had its dialect quote character escaped.
* **`em.find` / `qb.where` JSON-property filters** — `em.find(Entity, { jsonCol: { [userKey]: value } })`. The user-supplied JSON sub-keys cannot be validated against any metadata (JSON columns are schemaless by design), and were spliced into the SQL string literal of the JSON path expression without escaping.
* **`qb.where` / `qb.orderBy` / `qb.groupBy` / `qb.having` / `qb.select` keys** — keys containing `.` or `::` bypassed the structured-where metadata validator in `CriteriaNode`, then flowed through the same broken `quoteIdentifier`. Apps that forwarded raw filter keys from request input were already broken on authorization grounds (e.g. `{ isAdmin: true }`); the SQL injection here is a defence-in-depth failure on top of that.

The vulnerability does **not** affect documented escape-hatch APIs (`raw()`, the `sql` tagged template, `qb.raw()`, `em.raw()`) — those are documented as accepting raw SQL and are the application's responsibility to sanitize.

## Impact

* **Confidentiality** — read from any table/schema the database user has access to (cross-tenant data leak in multi-tenant deployments).
* **Integrity** — on dialects supporting multi-statement queries (MSSQL, MySQL with multi-statement enabled), execute additional arbitrary SQL statements (data modification, in-database privilege escalation).
* **Availability** — DROP/TRUNCATE via injected statements where the database user has the privilege.

## Affected dialects

All SQL dialects supported by MikroORM. The identifier-quoting bug exists in every dialect's `quoteIdentifier` (the dialect's own quote character — backtick, double quote, or right bracket — was not doubled when embedded in the identifier). The JSON-path bug exists in all dialects' `getSearchJsonPropertyKey`/`quoteJsonKey`.

MongoDB driver is **not** affected (no SQL).

## Patches

* v7: upgrade to **7.0.14** or later.
* v6: upgrade to **6.6.14** or later.

Patches:
* Identifier quoting: #7653 (master) / #7654 (6.x)
* JSON-path keys: #7656 (master) / #7657 (6.x)

## Workarounds

If users cannot upgrade immediately:

* For multi-tenant apps using `em.fork({ schema })` / `wrap().setSchema()` / `qb.withSchema()`: validate the schema name against a strict allowlist (e.g. `^[A-Za-z_][\w$]*$`) **before** passing it to MikroORM.
* For applications that pass `where` / `orderBy` filters from request input: validate every key against the entity's known properties before constructing the filter; do not pass keys containing `.` or `::` from user input.
* For applications that allow filtering on JSON columns from request input: validate every JSON sub-key against an allowlist (or against `^[a-zA-Z_][\w]*$`) before passing it to `em.find`.

## Credits

Reported and patched by Martin Adámek (project maintainer) during an internal security review.

## References
- https://github.com/mikro-orm/mikro-orm/security/advisories/GHSA-cfw5-68c4-ffqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44680
- https://github.com/mikro-orm/mikro-orm/pull/7653
- https://github.com/mikro-orm/mikro-orm/pull/7654
- https://github.com/mikro-orm/mikro-orm/pull/7656
- https://github.com/mikro-orm/mikro-orm/pull/7657
- https://github.com/mikro-orm/mikro-orm
