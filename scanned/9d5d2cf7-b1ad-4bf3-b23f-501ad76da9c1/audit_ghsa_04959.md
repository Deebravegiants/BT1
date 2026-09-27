# [H] Remark42: Cross-Site Scripting (XSS) on /api/v1/img via content-type spoofing

## Summary
Severity: High
Advisory: GHSA-4c8j-mgm4-qqvp
CVE: CVE-2026-48788
CWE: CWE-436, CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-4c8j-mgm4-qqvp
Type: github-advisory

## Affected
- Go: `github.com/umputun/remark42` — affected >=1.6.0 <1.16.0

## Details
### Summary
The remark42 image proxy fetches an arbitrary remote URL and re-serves the response from remark42's own origin. The download path decides whether the fetched resource is an image by looking only at the `Content-Type` header the remote server claims — it never inspects the actual bytes. The serving path then derives the response `Content-Type` by sniffing those bytes with `http.DetectContentType`.

An attacker hosts a URL that sets `Content-Type` to `image/png` but returns an HTML/JavaScript body:

* the download check sees `image/png` → accepts it;
* the serve path sniffs the body → emits `Content-Type: text/html`;
* the browser renders attacker HTML/JS as a document in remark42's origin.

### Details
#### Downloader

`backend/app/rest/proxy/image.go` — `downloadImage()`, lines 189-206:

```go
contentType := resp.Header.Get("Content-Type")
if !strings.HasPrefix(contentType, "image/") {
    return nil, fmt.Errorf("invalid content type %s", contentType)
}

maxSize := 5 * 1024 * 1024 // 5MB default
if p.ImageService != nil && p.ImageService.MaxSize > 0 {
    maxSize = p.ImageService.MaxSize
}
lr := io.LimitReader(resp.Body, int64(maxSize)+1)
imgData, err := io.ReadAll(lr)
if err != nil {
    return nil, fmt.Errorf("unable to read image body: %w", err)
}
if len(imgData) > maxSize {
    return nil, fmt.Errorf("image is too large")
}
return imgData, nil          // <-- bytes never validated, returned as-is
```

Send `Content-Type: image/png` and the check passes regardless of what the body actually contains.

#### Server

`backend/app/rest/proxy/image.go` — `Handler()`, line 131:

```go
w.Header().Add("Content-Type", p.ImageService.ImgContentType(img))
_, err = io.Copy(w, bytes.NewReader(img))
```

`backend/app/store/image/image.go` — `ImgContentType()`, lines 242-249:

```go
func (s *Service) ImgContentType(img []byte) string {
    contentType := http.DetectContentType(img)
    if contentType == "application/octet-stream" {
        return "image/*"
    }
    return contentType                 // <-- returns text/html for an HTML body
}
```

### PoC

```python
self.send_response(200)
self.send_header("Content-Type", "image/png")
self.send_header("Content-Length", str(len(body)))
self.end_headers()
self.wfile.write(body)            # body = <!DOCTYPE html><script>...</script>
```

Then have the victim open `https://<remark42-host>/api/v1/img?src=<base64(attacker-host)>` top-level.

### Impact
* The script can issue authenticated, same-origin API calls with `credentials: 'include'` — the JWT cookie is sent automatically.
* The script can read the `XSRF-TOKEN` cookie and re-send it as the `X-XSRF-TOKEN` header, defeating CSRF protection. The attacker acts as the victim: delete/edit their comments, change their settings, and — if the victim is admin — perform admin actions.

Triggering requires no remark42 account on the target instance; the attacker only needs to host the malicious upstream URL and deliver the proxy link to a victim by any means (email, DM, link on another site, etc.).

### Fix

`v1.16.0` adds layered defense to `/api/v1/img` and `/api/v1/picture/{user}/{id}`:

* `rest.SafeImgContentType` validates sniffed body bytes against a strict allowlist (`image/png`, `image/jpeg`, `image/gif`, `image/webp`, `image/bmp`, `image/x-icon`). Non-image content returns `415` with no body echo. SVG is implicitly excluded.
* Every response carries `Content-Security-Policy: default-src 'none'; sandbox; frame-ancestors 'none'`, `X-Content-Type Options: nosniff`, and `Content-Disposition: inline; filename="image"`.
* The ETag is bumped to `"v2:<base64(src)>"`. Browsers that revalidate cached pre-fix responses get a fresh validated `200` instead of a `304` against the poisoned cached entry.
* The strict `default-src 'none'; sandbox` CSP also applies to all `/api/v1/*` routes as defense-in-depth.

#### Residual exposure

Browser-local caches that already hold a pre-fix `text/html` response with `Cache-Control: max-age=2592000` keep serving it from local store until the TTL expires or the cache is evicted under memory pressure. The ETag bump only reaches clients that revalidate during the cached lifetime. Operators running a CDN/edge cache in front of remark42 should purge `/api/v1/img` after deploying `v1.16.0`.

## References
- https://github.com/umputun/remark42/security/advisories/GHSA-4c8j-mgm4-qqvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-48788
- https://github.com/umputun/remark42/commit/78d6de6bce1e961f023969da3ec8a00dd80c9ae8
- https://github.com/umputun/remark42
- https://github.com/umputun/remark42/releases/tag/v1.16.0
