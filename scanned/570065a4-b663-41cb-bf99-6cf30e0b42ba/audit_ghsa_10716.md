# [H] NocoBase Has SQL Injection via template variable substitution in workflow SQL node

## Summary
Severity: High
Advisory: GHSA-vx58-fwwq-5g8j
CVE: CVE-2026-34825
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-vx58-fwwq-5g8j
Type: github-advisory

## Affected
- npm: `@nocobase/plugin-workflow-sql` — affected >=0 <2.0.30

## Details
## Summary

NocoBase <= 2.0.8 `plugin-workflow-sql` substitutes template variables directly into raw SQL strings via `getParsedValue()` without parameterization or escaping. Any user who triggers a workflow containing a SQL node with template variables from user-controlled data can inject arbitrary SQL.

## Affected Versions

- Affected: all versions through 2.0.8

## Details

The `SQLInstruction` in `packages/plugins/@nocobase/plugin-workflow-sql/src/server/SQLInstruction.ts` line 28 processes SQL templates:

```typescript
// SQLInstruction.ts:28
const sql = processor.getParsedValue(node.config.sql || '', node.id).trim();
```

Then executes the resulting string directly:

```typescript
// SQLInstruction.ts:35
const [result] = await collectionManager.db.sequelize.query(sql, {
  transaction: this.workflow.useDataSourceTransaction(dataSourceName, processor.transaction),
});
```

`getParsedValue()` performs simple string substitution of `{{$context.data.fieldName}}` placeholders with values from the workflow trigger data. No escaping, quoting, or parameterized binding is applied.

When an admin creates a SQL node with a template like:
```sql
SELECT * FROM users WHERE nickname = '{{$context.data.nickname}}'
```

Any user who triggers the workflow with a crafted value can break out of the string literal and inject arbitrary SQL.

## Proof of Concept

1. Login as admin
2. Create a collection-trigger workflow on the `users` table (mode: after create)
3. Add a SQL node with:
```sql
SELECT id, nickname, email FROM users WHERE nickname = '{{$context.data.nickname}}'
```
4. Enable the workflow
5. Create a user with nickname set to: `' UNION SELECT 1,version(),current_user --`
6. Check execution result:

```json
[
  {
    "id": 1,
    "nickname": "PostgreSQL 16.13 (Debian 16.13-1.pgdg13+1) on x86_64-pc-linux-gnu...",
    "email": "nocobase"
  }
]
```

The injected UNION SELECT returned the database version and current database user.

## Impact

Full database read/write access through SQL injection. An attacker who can trigger a workflow with a SQL node containing template variables from user-controlled data can extract credentials, modify records, or drop tables. The severity depends on the database user's privileges (full superuser access in the default Docker deployment).

## Suggested Fix

Use parameterized queries. Replace direct string substitution with Sequelize bind parameters:

```diff
// SQLInstruction.ts
- const sql = processor.getParsedValue(node.config.sql || '', node.id).trim();
+ const { sql, bind } = processor.getParsedValueAsParams(node.config.sql || '', node.id);
  const [result] = await collectionManager.db.sequelize.query(sql, {
+   bind,
    transaction: ...
  });
```

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-vx58-fwwq-5g8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34825
- https://github.com/nocobase/nocobase/commit/75da3dddc4aba739c398f7072725dcf7f5487f5c
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.0.30
