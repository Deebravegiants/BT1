# [H] budibase: Database Connector SQL Injections in PostgreSQL, MS SQL, and MySQL

## Summary
Severity: High
Advisory: GHSA-qqf5-x7mj-v43p
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-qqf5-x7mj-v43p
Type: github-advisory

## Affected
- npm: `budibase` — affected >=0 <3.39.19

## Details
### Summary
This advisory covers three distinct SQL Injection vulnerabilities within Budibase's database connectors (PostgreSQL, Microsoft SQL Server, and MySQL). Because user-controlled schema and table configurations are interpolated directly into raw SQL queries without proper escaping or parameterization during database introspection, an authenticated administrator can break out of string delimiters. This allows for arbitrary DDL/DML execution, database compromise, and potential underlying OS command execution (e.g., via MS SQL `xp_cmdshell`).

### Details

### Vulnerability Type & Title
**PostgreSQL `SET search_path` SQL Injection**

### Description & Root Cause
The `schema` datasource config field is interpolated directly into a raw SQL statement without proper escaping. Double quotes inside the schema name are not escaped, allowing an attacker to break out of the string literal and inject arbitrary SQL.

**Vulnerable Code:**
**File:** `packages/server/src/integrations/postgres.ts`, lines 355–358

```typescript
const search_path = this.config.schema
  .split(",")
  .map(item => `"${item.trim()}"`)                // NO escaping of embedded "
await this.client.query(`SET search_path TO ${search_path.join(",")};`)
```

`node-postgres` sends this via the **simple query protocol**, which supports multi-statement execution with semicolons.

### Step-by-Step Reproduction
1. Edit a PostgreSQL datasource configuration.
2. Set the schema field to:
   `public"; CREATE TABLE pwned AS SELECT usename, passwd FROM pg_shadow; --`
3. Save or trigger a connection test.
4. The query executes as:
   `SET search_path TO "public"; CREATE TABLE pwned AS SELECT usename, passwd FROM pg_shadow; --;`
5. PostgreSQL executes both statements.

### Impact
- Full database compromise. The attacker can read `pg_shadow` hashes, call `pg_read_file()`, or execute any DDL/DML.

---

### Vulnerability Type & Title
**Microsoft SQL Server Schema Introspection SQL Injection**

### Description & Root Cause
Three methods used during schema introspection (`buildSchema`) interpolate user-controlled values directly into SQL strings using single-quote delimiters with no escaping.

**Vulnerable Code:**
**File:** `packages/server/src/integrations/microsoftSqlServer.ts`, lines 388–414

```typescript
getDefinitionSQL(tableName: string, schemaName: string) {
  return `select * from INFORMATION_SCHEMA.COLUMNS
          where TABLE_NAME='${tableName}' AND TABLE_SCHEMA='${schemaName}'`
}
```

`schemaName` comes directly from `this.config.schema` (user config).

### Step-by-Step Reproduction
1. Edit an MS SQL Server datasource configuration.
2. Set the schema field to: `dbo'; EXEC xp_cmdshell('whoami'); --`
3. Trigger schema introspection (fetch tables).
4. The OS command executes on the SQL server if `xp_cmdshell` is enabled.

### Impact
- Arbitrary SQL execution, potentially leading to OS command execution via `xp_cmdshell`.

---

### Vulnerability Type & Title
**MySQL `multipleStatements: true` + `DESCRIBE` Backtick Injection**

### Description & Root Cause
The MySQL integration enables `multipleStatements: true`, allowing semicolon-separated multi-statement execution. When introspecting tables, table names are interpolated into a `DESCRIBE` query wrapped in backticks, but the backticks are not escaped.

**Vulnerable Code:**
**File:** `packages/server/src/integrations/mysql.ts`, lines 172, 305

```typescript
this.config = { ...config, multipleStatements: true, ... }  // line 172
...
{ sql: `DESCRIBE \`${tableName}\`;` }  // line 305 — backtick NOT escaped
```

### Step-by-Step Reproduction
1. An attacker (or malicious database user) creates a table named ``foo`; DROP TABLE users; --``.
2. In Budibase, an admin triggers schema introspection for the database.
3. Budibase reads the malicious table name from `INFORMATION_SCHEMA.TABLES` and inserts it into the `DESCRIBE` query.
4. The backtick breaks out, and the secondary `DROP TABLE` payload executes.

### Impact
- Arbitrary SQL execution triggered during schema discovery. Requires prior database catalog manipulation.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-qqf5-x7mj-v43p
- https://github.com/Budibase/budibase
