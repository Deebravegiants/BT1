# [M] GoFiber Vulnerable to X-Real-IP Spoofing via Header.Add() in BalancerForward

## Summary
Severity: Medium
Advisory: GHSA-gcfq-8gqf-4876
CVE: CVE-2026-45045
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-gcfq-8gqf-4876
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v3` — affected >=0 <3.3.0
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.52.14

## Details
## Summary

The `BalancerForward` proxy helper in GoFiber uses `Header.Add()` instead of `Header.Set()` when injecting the `X-Real-IP` header. This appends the real client IP as a second header value rather than replacing any attacker-supplied value. Upstream servers that read the first `X-Real-IP` header (nginx, Express, most HTTP servers) use the attacker's spoofed IP for logging, rate limiting, and access control.

## Vulnerable Code

**File:** `middleware/proxy/proxy.go`, lines 270-285

```go
func BalancerForward(servers []string, clients ...*fasthttp.Client) fiber.Handler {
    r := &roundrobin{
        current: 0,
        pool:    servers,
    }
    return func(c fiber.Ctx) error {
        server := r.get()
        if !strings.HasPrefix(server, "http") {
            server = "http://" + server
        }
        c.Request().Header.Add("X-Real-IP", c.IP())   // line 282: Add, not Set
        return Do(c, server+c.OriginalURL(), clients...)
    }
}
```

## Data Flow

1. Attacker sends request with `X-Real-IP: 10.0.0.1` (spoofed internal IP)
2. `BalancerForward` handler executes at line 282
3. `c.Request().Header.Add("X-Real-IP", c.IP())` APPENDS the real IP as a second header
4. Upstream server receives: `X-Real-IP: 10.0.0.1` AND `X-Real-IP: <real-attacker-ip>`
5. Most HTTP servers (nginx, Node.js, Apache) read the FIRST value
6. Upstream uses `10.0.0.1` for all IP-dependent logic

## Impact

- **Rate limit bypass:** IP-based rate limiting at the upstream uses the spoofed IP, allowing unlimited requests
- **IP ACL bypass:** Internal IP allowlists (e.g., admin panels restricted to `10.0.0.0/8`) can be bypassed
- **Audit log poisoning:** Security logs record the spoofed IP, making incident investigation unreliable
- **Geolocation bypass:** IP-based geofencing or region restrictions are circumvented

## Fix

Replace `Header.Add()` with `Header.Set()` at line 282:

```go
c.Request().Header.Set("X-Real-IP", c.IP())
```

`Header.Set()` replaces any existing header value, ensuring only the real client IP is forwarded.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-gcfq-8gqf-4876
- https://nvd.nist.gov/vuln/detail/CVE-2026-45045
- https://github.com/gofiber/fiber/pull/4260
- https://github.com/gofiber/fiber/pull/4495
- https://github.com/gofiber/fiber/commit/1403cc8292da3220e9316960b4030cc722a0f396
- https://github.com/gofiber/fiber/commit/33c9501288ab47a429c8b5e701493f0c3c0af37d
- https://github.com/gofiber/fiber
- https://github.com/gofiber/fiber/releases/tag/v2.52.14
- https://github.com/gofiber/fiber/releases/tag/v3.3.0
