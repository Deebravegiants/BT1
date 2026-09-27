# [H] chi Middleware Vulnerable to Potential IP Spoofing via `X-Forwarded-For` Header in `Request.RemoteAddr` Resolution

## Summary
Severity: High
Advisory: GHSA-9g5q-2w5x-hmxf
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-9g5q-2w5x-hmxf
Type: github-advisory

## Affected
- Go: `github.com/go-chi/chi/middleware` — affected >=0.9.0
- Go: `github.com/go-chi/chi/v2/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v3/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v4/middleware` — affected >=0
- Go: `github.com/go-chi/chi/v5/middleware` — affected >=0 <5.3.0

## Details
### Summary
The vulnerability allows the `Request.RemoteAddr` to be spoofed when determining the request source IP via the `X-Forwarded-For` header. This could result in misidentification of the request source and potentially compromise access control and logging integrity.

### Details
Currently, the `RealIP()` implementation splits the `X-Forwarded-For` header by `,` and uses the first IP.
https://github.com/go-chi/chi/blob/v5.1.0/middleware/realip.go#L50-L54

However, relying on the first IP in the `X-Forwarded-For` header is insecure because it can be manipulated by attackers to falsify the source IP.

Malicious Case:
1. A malicious client sends a request with a forged IP in the X-Forwarded-For header: `X-Forwarded-For: <forged-ip>`
2. The proxy appends the actual client’s IP and forwards the request: `X-Forwarded-For: <forged-ip>,<client-ip>`
3. If the server always uses the first IP, it becomes vulnerable to IP spoofing.

Ideally, the implementation should verify IPs starting from the end of the `X-Forwarded-For` header value, skipping trusted IPs within the system, and using the first untrusted IP as the actual client IP.

For example, the `labstack/echo` web framework processes the `X-Forwarded-For` header by checking IPs from the end, skipping trusted IPs, and using the first untrusted IP as the client's ip.
https://github.com/labstack/echo/blob/v4.13.2/ip.go#L261-L273

### PoC
#### 1. Run the Go application with the following code:
```go
package main

import (
    "fmt"
    "log"
    "net/http"

    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    // Set handler to print the remote address
    handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintln(
            w,
            fmt.Sprintf("remote addr: %s (want 192.0.2.1)", r.RemoteAddr),
        )
    })
    // Use RealIP middleware
    log.Fatal(http.ListenAndServe(":8080", middleware.RealIP(handler)))
}
```
#### 2. Send a request to the server using curl with a manipulated X-Forwarded-For header:
```
$ curl localhost:8080 -H 'X-Forwarded-For: 192.0.2.2, 192.0.2.1'
remote addr: 192.0.2.2 (want 192.0.2.1)
```

### Impact
This vulnerability can lead to a request source IP spoofing issue, which may allow attackers to bypass access controls or falsify request logs. It primarily affects systems that rely on X-Forwarded-For to determine the actual client IP, particularly in scenarios where intermediary proxies or load balancers are involved.

## References
- https://github.com/go-chi/chi/security/advisories/GHSA-9g5q-2w5x-hmxf
- https://github.com/go-chi/chi
- https://github.com/go-chi/chi/releases/tag/v5.3.0
