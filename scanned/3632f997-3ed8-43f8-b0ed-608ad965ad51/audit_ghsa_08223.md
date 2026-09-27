# [H] Argo Vulnerable to Unauthenticated Memory Exhaustion (DoS) in Webhook Interceptor

## Summary
Severity: High
Advisory: GHSA-jcc8-g2q4-9fxq
CVE: CVE-2026-42294
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-jcc8-g2q4-9fxq
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=0 <3.7.14
- Go: `github.com/argoproj/argo-workflows/v4` — affected >=4.0.0 <4.0.5

## Details
**Severity:** Medium
**Component:** Webhook Interceptor (`server/auth/webhook`)
**Vulnerability Type:** Denial of Service (DoS)

## Description
The Webhook Interceptor loads the entire request body into memory before authenticating the request or verifying its signature. This occurs on the `/api/v1/events/` endpoint, which is publicly accessible (albeit intended for webhooks). An attacker can send a request with an extremely large body (e.g., multiple gigabytes), causing the Argo Server to allocate excessive memory, potentially leading to an Out-Of-Memory (OOM) crash and denial of service.

## Vulnerable Code
In `server/auth/webhook/interceptor.go`:
```go
func (i *WebhookInterceptor) addWebhookAuthorization(r *http.Request, kube kubernetes.Interface) error {
    // ... basic checks ...
    
    // Vulnerability: Reads entire body into memory unconditionally
    buf, _ := io.ReadAll(r.Body)
    defer func() { r.Body = io.NopCloser(bytes.NewBuffer(buf)) }()
    
    // ... subsequent logic finds correct service account and secret ...
    // ... verification happens later ...
}
```
The `io.ReadAll` call happens before the signature verification loop.

## Impact
- **Service Availability:** An attacker can crash the Argo Server, disrupting workflow execution and API access for all users.

## PoC (Conceptual)
1.  Target the webhook endpoint: `POST /api/v1/events/some-namespace`
2.  Send a `Content-Length: 1000000000` (1GB) header.
3.  Stream 1GB of random data.
4.  Monitor server memory usage. It will spike until 1GB is allocated or the process crashes.

## Recommendation
1.  **Limit Body Size:** Enforce a strict limit on webhook body size (e.g., 10MB) using `http.MaxBytesReader`.
2.  **Streaming Verification:** If possible, verify the signature in a streaming fashion or use a temporary file for large payloads (though typically webhooks are small).

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-jcc8-g2q4-9fxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42294
- https://github.com/argoproj/argo-workflows/commit/7abb4de6c3599e2d5d960ba4d5de4cf1df109965
- https://access.redhat.com/security/cve/CVE-2026-42294
- https://bugzilla.redhat.com/show_bug.cgi?id=2468443
- https://github.com/argoproj/argo-workflows
- https://github.com/argoproj/argo-workflows/releases/tag/v3.7.14
- https://github.com/argoproj/argo-workflows/releases/tag/v4.0.5
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42294.json
