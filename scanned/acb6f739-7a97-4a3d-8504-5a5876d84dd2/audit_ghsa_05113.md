# [M] Gogs's Unauthenticated Jupyter Notebook (ipynb) Sanitizer allows arbitrary data: URIs leading to XSS

## Summary
Severity: Medium
Advisory: GHSA-3w28-36p9-w929
CVE: CVE-2026-52816
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-3w28-36p9-w929
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

The Jupyter Notebook (ipynb) sanitizer endpoint at `POST /-/api/sanitize_ipynb` allows arbitrary `data:` URIs without proper restrictions, potentially leading to Cross-Site Scripting (XSS). The endpoint uses `bluemonday.UGCPolicy()` with `p.AllowURLSchemes("data")` which permits all data URI schemes including `data:text/html`, enabling attackers to inject malicious HTML/JavaScript. Additionally, the endpoint has no authentication middleware, allowing any registered user to exploit this vulnerability.

## Severity

**High**

## Affected Versions

All versions using the vulnerable endpoint

## Vulnerability Details

- **CVE ID**: (To be assigned)
- **Entry Point**: `POST /-/api/sanitize_ipynb`
- **Attack Vector**: Network
- **Authentication Required**: No (only needs a registered user account)

## Impact

An attacker with a registered user account can:

- Send malicious HTML containing `data:text/html` URIs to the sanitization endpoint
- Receive sanitized but attacker-controlled HTML in the response
- Execute arbitrary JavaScript in the attacker's browser context through XSS
- Potentially exploit other users if the sanitized output is rendered in their context

The vulnerability has higher severity because:

1. No authentication required (only needs a registered user account)
2. Unlike the safer pattern in `internal/markup/sanitizer.go:39` which uses `isSafeDataURI` to only allow safe image MIME types, this endpoint allows ALL data URIs including HTML
3. The returned HTML can be used to craft XSS attacks

## Proof of Concept

Attacker sends a POST request to the sanitization endpoint:

```http
POST /-/api/sanitize_ipynb HTTP/1.1
Host: target.gogs.instance
Content-Type: text/plain

<a href="data:text/html,<script>alert(document.cookie)</script>">click</a>
```

The server returns the sanitized HTML with the data URI preserved:

```html
<a href="data:text/html,<script>alert(document.cookie)</script>">click</a>
```

When this HTML is rendered in a browser, the JavaScript within the data URI will execute, leading to XSS.

## Affected Component

**File**: `internal/app/api.go:10-16`

```go
func ipynbSanitizer() *bluemonday.Policy {
	p := bluemonday.UGCPolicy()
	p.AllowAttrs("class", "data-prompt-number").OnElements("div")
	p.AllowAttrs("class").OnElements("img")
	p.AllowURLSchemes("data")  // <-- VULNERABLE: allows all data URIs
	return p
}
```

**File**: `cmd/gogs/web.go:681-683` - No authentication middleware

```go
m.Group("/-", func() {
	m.Get("/metrics", app.MetricsFilter(), promhttp.Handler())
	m.Group("/api", func() {
		m.Post("/sanitize_ipynb", app.SanitizeIpynb())  // <-- No auth middleware
	})
})
```

## Root Cause

1. **Unrestricted data URI scheme**: The code at `internal/app/api.go:14` uses `p.AllowURLSchemes("data")` without any restriction, unlike the safer implementation in `internal/markup/sanitizer.go:39` which uses `AllowURLSchemeWithCustomPolicy("data", isSafeDataURI)` to only allow safe image MIME types.

2. **No authentication**: The endpoint at `cmd/gogs/web.go:682` does not have any authentication middleware applied, making it accessible to any registered user.

3. **Insufficient validation**: The sanitization only removes dangerous tags/attributes but preserves data URIs, allowing `data:text/html` payloads to pass through.

## Suggested Fix

**Option 1**: Use the same safe pattern as `internal/markup/sanitizer.go`

Replace `p.AllowURLSchemes("data")` with:

```go
p.AllowURLSchemeWithCustomPolicy("data", isSafeDataURI)
```

Where `isSafeDataURI` is a function that only allows safe image MIME types (image/png, image/jpeg, image/gif, etc.).

**Option 2**: Add authentication middleware

Apply appropriate authentication to the endpoint:

```go
m.Post("/sanitize_ipynb", middleware.signIn, app.SanitizeIpynb())
```

**Option 3**: Disable data URI scheme entirely

If data URIs are not required for ipynb sanitization:

```go
// Remove this line entirely:
// p.AllowURLSchemes("data")
```

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-3w28-36p9-w929
- https://nvd.nist.gov/vuln/detail/CVE-2026-52816
- https://github.com/gogs/gogs/pull/8326
- https://github.com/gogs/gogs/commit/dd1bd9837aa196b3ed3a8ee21e5727b5d7a986a3
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
