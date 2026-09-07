# [H] Budibase: MySQL DESCRIBE Backtick Injection via multipleStatements in Database Connector

## Summary
Severity: High
Advisory: GHSA-2xgg-r2wc-c5r2
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-2xgg-r2wc-c5r2
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0

## Details
### Summary
**This is a related but independently fixable vulnerability to GHSA-qqf5-x7mj-v43p
(PostgreSQL SQL injection), reported in the same original disclosure and
split per GitHub CNA guidance (rule 4.2.11) since it affects a separate
integration, has a distinct attack precondition, and requires a separate
patch.**

The MySQL integration enables `multipleStatements: true` on the connection,
permitting semicolon-separated multi-statement execution. During table
introspection, table names retrieved from `INFORMATION_SCHEMA.TABLES` are
interpolated into a `DESCRIBE` query wrapped in backticks, but embedded
backticks in the table name are never escaped — allowing a malicious table
name to break out and inject a second, attacker-controlled statement.

### Details

**Vulnerable Code:**
File: `packages/server/src/integrations/mysql.ts`, lines 172, 305

```typescript
this.config = { ...config, multipleStatements: true, ... }  // line 172
...
{ sql: `DESCRIBE \`${tableName}\`;` }  // line 305 — backtick NOT escaped
```

Because `multipleStatements` is enabled, any statement appended after the
backtick break-out executes as a second query in the same round trip.

### Step-by-Step Reproduction
1. An attacker with the ability to create tables in the target MySQL
   database (e.g. a lower-privileged database user, or a malicious actor in
   a multi-tenant database) creates a table named:
   ``foo`; DROP TABLE users; --``
2. In Budibase, an administrator triggers schema introspection for that
   database (e.g. opening the datasource or refreshing its table list).
3. Budibase reads the malicious table name from `INFORMATION_SCHEMA.TABLES`
   and interpolates it into the `DESCRIBE` query.
4. The unescaped backtick terminates the identifier early, and the
   semicolon-separated payload (enabled by `multipleStatements: true`)
   executes as a second statement.

### Impact
Arbitrary SQL execution triggered during routine schema discovery. Unlike
the PostgreSQL and MS SQL Server findings, this does not require the
attacker to control the Budibase datasource configuration directly — only
the ability to create a maliciously named table in the underlying database
beforehand, with an administrator's normal use of the introspection feature
serving as the trigger.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-2xgg-r2wc-c5r2
- https://github.com/Budibase/budibase/pull/18989
- https://github.com/Budibase/budibase/commit/2c61f389c9986c91ddd8ae161c2b5e8ec21c60ac
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.39.18
