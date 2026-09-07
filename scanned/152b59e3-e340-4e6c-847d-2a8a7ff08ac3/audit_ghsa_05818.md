# [H] Echo: Encoded slash (%2F) bypasses route-level protection and exposes static files

## Summary
Severity: High
Advisory: GHSA-vfp3-v2gw-7wfq
CVE: CVE-2026-55677
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-vfp3-v2gw-7wfq
Type: github-advisory

## Affected
- Go: `github.com/labstack/echo/v5` — affected >=0 <5.2.0
- Go: `github.com/labstack/echo/v4` — affected >=0 <4.15.3
- Go: `github.com/labstack/echo` — affected >=0

## Details
### Summary

Echo's router and static file handler disagree on URL path decoding. The router matches routes using the raw encoded path (preserving `%2F` as-is), while `StaticDirectoryHandler` unescapes `%2F` to `/` before resolving filesystem paths. This allows an attacker to bypass route-level access controls and read static files without authorization.

### Details

**Root cause 1 — `router.go` lines 798-802:**
The router uses `req.URL.RawPath` for route matching when `useEscapedPathForRouting` is false (the default). This means `/admin%2Fsecret.txt` is treated as a single path segment and does NOT match the `/admin/*` route pattern.

```go
if !r.useEscapedPathForRouting && req.URL.RawPath != "" {
    path = req.URL.RawPath
}
```

**Root cause 2 — `echo.go` lines 559-568:**
`StaticDirectoryHandler` calls `url.PathUnescape()` on the path parameter before opening files. This converts `%2F` back to `/`, resolving `admin/secret.txt` on disk.

```go
if !disablePathUnescaping {
    tmpPath, err := url.PathUnescape(p)
    p = tmpPath
}
name := filepath.ToSlash(filepath.Clean(strings.TrimPrefix(p, "/")))
```

### PoC (Screenshot)
Sample:
<img width="1291" height="970" alt="image" src="https://github.com/user-attachments/assets/0bc58059-3e6d-4678-ab25-a5c79b006738" />

403:
<img width="526" height="194" alt="image" src="https://github.com/user-attachments/assets/2f55ffdd-87b2-4a1b-8a13-130ebad0f257" />

Bypass with encoded slash:
<img width="592" height="203" alt="image" src="https://github.com/user-attachments/assets/1191cd39-ae8f-4d7e-8fb1-cb9cf31f484f" />

### Impact

Unauthorized static file disclosure. Applications that protect route prefixes with authentication middleware while also serving static files from a broader root are vulnerable. An attacker only needs to encode the slash (`/` → `%2F`) in the URL to bypass all route-level protection.

Common affected pattern:
```go
adminGroup := e.Group("/admin", authMiddleware)
e.StaticFS("/", os.DirFS("public"))
```

## References
- https://github.com/labstack/echo/security/advisories/GHSA-vfp3-v2gw-7wfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-55677
- https://github.com/labstack/echo/pull/3009
- https://github.com/labstack/echo/pull/3011
- https://github.com/labstack/echo/commit/8d1ae9d3360a71672418856d58753af25f2c3986
- https://github.com/labstack/echo/commit/c3fa2a27ff92b2b8db360de614f999ef1da24725
- https://github.com/labstack/echo
- https://github.com/labstack/echo/releases/tag/v4.15.3
- https://github.com/labstack/echo/releases/tag/v5.2.0
