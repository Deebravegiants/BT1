# [H] Traefik: Pre-authentication decision bypass due to forwarded alias spoofing

## Summary
Severity: High
Advisory: GHSA-5m6w-wvh7-57vm
CVE: CVE-2026-39858
CWE: CWE-290, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-5m6w-wvh7-57vm
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-rc.2
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta1 <3.6.14
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.43
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a high severity authentication bypass vulnerability in Traefik's `ForwardAuth` and snippet-based authentication middleware. Traefik's forwarded-header sanitization logic targets only canonical header names (e.g., `X-Forwarded-Proto`) and does not strip or normalize alias variants that use underscores instead of dashes (e.g., `X_Forwarded_Proto`). These unsanitized alias headers are forwarded intact to the authentication backend. When the backend normalizes underscore and dash header forms equivalently, an attacker can inject spoofed trust context — such as a trusted scheme or host — through the alias headers and bypass authentication on protected routes without valid credentials.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
An authentication bypass arises from chaining two bugs: incomplete forwarded-header sanitization at ingress and overly permissive header forwarding in pre-auth subrequests. While canonical `X-Forwarded-*` headers are handled, alias variants (e.g., underscore forms) are neither normalized nor stripped consistently. When downstream auth services normalize these headers, attackers can inject trusted context and bypass authentication on protected routes without credentials.

### Details
This issue results from the interaction between forwarded-header handling and auth subrequest construction, creating a trust boundary mismatch.

At ingress, Traefik defines a fixed set of canonical forwarded headers (`X-Forwarded-Proto`, `X-Forwarded-For`, etc.):

Reference : [`pkg/middlewares/forwardedheaders/forwarded_header.go#L29-L36`](https://github.com/traefik/traefik/blob/174e5d81111d8e9fb3d3c81cf6d22f3e33eb4f78/pkg/middlewares/forwardedheaders/forwarded_header.go#L29-L36)

```go
var xHeaders = []string{
	xForwardedProto,
	xForwardedFor,
	xForwardedHost,
	xForwardedPort,
```

This logic focuses exclusively on canonical header names and does not account for alias forms such as `X_Forwarded_Proto`. As a result, while standard headers may be sanitized or rewritten, semantically equivalent variants can pass through unchanged.

During ForwardAuth processing, request headers are copied wholesale into the auth subrequest:

Reference : [`pkg/middlewares/auth/forward.go#L401-L408`](https://github.com/traefik/traefik/blob/174e5d81111d8e9fb3d3c81cf6d22f3e33eb4f78/pkg/middlewares/auth/forward.go#L401-L408)

```go
utils.CopyHeaders(forwardReq.Header, req.Header)
RemoveConnectionHeaders(forwardReq)
utils.RemoveHeaders(forwardReq.Header, hopHeaders...)
```

This implementation forwards nearly all client-supplied headers to the auth backend, with filtering limited to hop-by-hop headers. There is no normalization or deduplication between canonical and alias header forms, meaning attacker-controlled headers can reach the auth service intact.

A similar pattern exists in snippet-based auth:

Reference : [`pkg/middlewares/ingressnginx/snippet/snippet.go#L574-L581`](https://github.com/traefik/traefik/blob/174e5d81111d8e9fb3d3c81cf6d22f3e33eb4f78/pkg/middlewares/ingressnginx/snippet/snippet.go#L574-L581)

```go
utils.CopyHeaders(forwardReq.Header, req.Header)
RemoveConnectionHeaders(forwardReq)
utils.RemoveHeaders(forwardReq.Header, hopHeaders...)
```

Again, headers are forwarded without enforcing a consistent trust model or canonicalization.

The vulnerability emerges when the auth backend normalizes header names (e.g., treating `X_Forwarded_Proto` and `X-Forwarded-Proto` equivalently). In that case:

- Traefik sanitizes only canonical headers.
- Alias headers remain attacker-controlled.
- The auth service merges or evaluates these aliases during normalization.
- Trust predicates (e.g., scheme = HTTPS, trusted host) are satisfied using spoofed values.

This allows a single crafted request to simultaneously bypass ingress trust enforcement and satisfy authentication checks, resulting in unauthorized access to protected backends.

### PoC

1. Configure a protected route using ForwardAuth or snippet-based auth, with an auth backend that normalizes header names (underscore ↔ dash).
2. Send a control request (expected: denied):

```http
GET / HTTP/1.1
Host: target.local
User-Agent: poc-control
Connection: close
```

3. Send an exploit request with alias headers (expected: allowed):

```http
GET /protected HTTP/1.1
Host: app.example.local
X_Forwarded_Proto: https
X_Forwarded_Host: trusted.example
Connection: close
```

### Impact
This vulnerability allows unauthenticated attackers to bypass authentication at the proxy-to-auth boundary by injecting spoofed trust context through header aliases. In deployments where authorization decisions depend on forwarded headers, attackers can access protected endpoints and interact with backend services as if they were fully authenticated. This effectively undermines ForwardAuth and similar mechanisms, potentially exposing sensitive internal functionality and data.

### Suggested Remediation
1. Strip and regenerate both canonical and alias forms of forwarded headers consistently at ingress and during auth subrequests.
2. Apply a unified normalization policy across all forwarded header families (including RFC7239 and `X-Forwarded-*`).
3. Restrict which headers are forwarded to auth services (prefer explicit allowlists).
4. Add regression tests covering alias normalization inconsistencies across common backend frameworks.

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-5m6w-wvh7-57vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-39858
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2
