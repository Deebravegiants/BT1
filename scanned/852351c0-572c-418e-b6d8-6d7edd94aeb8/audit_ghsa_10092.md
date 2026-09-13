# [H] SiYuan: Path Traversal via Double URL Encoding in `/export/` Endpoint (Incomplete Fix Bypass for CVE-2026-30869)

## Summary
Severity: High
Advisory: GHSA-hjh7-r5w8-5872
CVE: CVE-2026-41894
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-hjh7-r5w8-5872
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <3.6.5

## Details
### Summary
The fix for CVE-2026-30869 in SiYuan v3.5.10 only added a denylist check (`IsSensitivePath`) but did not address the root cause — a redundant `url.PathUnescape()` call in `serveExport()`. An authenticated attacker can use double URL encoding (`%252e%252e`) to traverse directories and read arbitrary workspace files including the full SQLite database (`siyuan.db`), kernel log, and all user documents.

### Details
In `kernel/server/serve.go`, the `serveExport()` function (line 314-320) processes file paths as follows:

```go
filePath := strings.TrimPrefix(c.Request.URL.Path, "/export/")
decodedPath, err := url.PathUnescape(filePath)     // second decode
fullPath := filepath.Join(exportBaseDir, decodedPath)
```

Go's HTTP server already decodes percent-encoded characters once during request parsing. The additional `url.PathUnescape()` call creates a double-decode vulnerability:

1. Attacker sends: `GET /export/%252e%252e/siyuan.db`
2. Go HTTP decodes `%25` → `%`, result: `URL.Path = /export/%2e%2e/siyuan.db`
3. Go's path cleaner sees `%2e%2e` as literal characters (not `..`), no redirect occurs
4. `url.PathUnescape("%2e%2e")` decodes to `..`
5. `filepath.Join(exportBaseDir, "../siyuan.db")` resolves to `<workspace>/temp/siyuan.db`

The CVE-2026-30869 fix added `IsSensitivePath()` which blocks `<workspace>/conf/` and OS-level paths (`/etc`, `/root`, etc.). However, it does NOT block:
- `<workspace>/temp/siyuan.db` — full document database
- `<workspace>/temp/blocktree.db` — block tree database
- `<workspace>/temp/siyuan.log` — kernel log
- `<workspace>/temp/asset_content.db` — asset content database

Note: the `/appearance/` handler in the same file correctly uses `gulu.File.IsSubPath()` to validate paths (line 447), but this check is missing from the `/export/` handler.

### PoC
[poc.zip](https://github.com/user-attachments/files/26866234/poc.zip)
Please extract the uploaded compressed file before proceeding

1. docker compose up -d --build
2. sh poc.sh

<img width="550" height="184" alt="스크린샷 2026-04-19 오후 5 08 30" src="https://github.com/user-attachments/assets/6aea4334-0b5a-4f45-bd1f-ecfad61ba524" />




### Impact
- Data exfiltration: An authenticated user (including low-privilege Publish/Reader users via the Publish service) can download the entire SQLite document database containing all blocks, documents, attributes, and full-text search indexes.
- Information disclosure: Kernel log (`siyuan.log`) leaks internal server paths, versions, configuration details, and error messages.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-hjh7-r5w8-5872
- https://nvd.nist.gov/vuln/detail/CVE-2026-41894
- https://github.com/siyuan-note/siyuan/commit/bb481e1290c4a34255652ede85a546504505d2a7
- https://github.com/advisories/GHSA-2h2p-mvfx-868w
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.5
