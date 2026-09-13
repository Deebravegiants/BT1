# [M] GoFiber never set HSTS header in helmet middleware due to incorrect protocol check

## Summary
Severity: Medium
Advisory: GHSA-gv83-gqw6-9j2c
CVE: CVE-2026-53624
CWE: CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-gv83-gqw6-9j2c
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber` — affected >=0 <3.4.0

## Details
### Summary

The `helmet` middleware in gofiber/fiber never sets the `Strict-Transport-Security` (HSTS) response header, even when `HSTSMaxAge` is explicitly configured, because the condition check at `helmet.go:67` uses `c.Protocol()` — which returns the HTTP protocol version string (e.g., `"HTTP/1.1"`, `"HTTP/2.0"`) — instead of `c.Scheme()` — which returns the URL scheme (`"http"` or `"https"`). Since `c.Protocol()` never equals `"https"` in any real deployment, the HSTS header is permanently disabled, defeating the security protection.

### Details

**Root cause:** `middleware/helmet/helmet.go`, line 67:

```go
if c.Protocol() == "https" && cfg.HSTSMaxAge != 0 {
```

`c.Protocol()` (defined at `req.go:865-867`) delegates to `fasthttp.Request.Header.Protocol()`, which returns the HTTP protocol version:
- `"HTTP/1.1"` for HTTP/1.1 connections
- `"HTTP/2.0"` for HTTP/2 connections

The correct method is `c.Scheme()` (defined at `req.go:844-862`), which returns:
- `"http"` for plain HTTP connections
- `"https"` for TLS connections

Since `"HTTP/1.1" != "https"` always evaluates to `true`, the entire HSTS block (lines 67-76) is dead code.

**Note on test coverage:** The existing helmet test (`helmet_test.go`) passes because it uses `ctx.Request.Header.SetProtocol("https")` to artificially force `Protocol()` to return `"https"`. However, `fasthttp.Request.Header.SetProtocol()` sets the HTTP version field, and real HTTP requests never have protocol `"https"` — they have `"HTTP/1.1"` or `"HTTP/2.0"`. The test is validating the wrong thing.

### PoC

**Clean-checkout maintainer-runnable recipe:**

1. Save the following as `middleware/helmet/poc_hsts_test.go`:

```go
package helmet

import (
    "crypto/tls"
    "net/http/httptest"
    "testing"

    "github.com/gofiber/fiber/v3"
)

func Test_PoC_HSTS_NeverSet(t *testing.T) {
    app := fiber.New()
    app.Use(New(Config{
        HSTSMaxAge: 31536000,
    }))
    app.Get("/", func(c fiber.Ctx) error {
        return c.SendString("ok")
    })

    // Simulate HTTPS connection
    req := httptest.NewRequest(fiber.MethodGet, "/", nil)
    req.TLS = &tls.ConnectionState{}

    resp, _ := app.Test(req)
    hsts := resp.Header.Get("Strict-Transport-Security")

    if hsts == "" {
        t.Log("BUG CONFIRMED: HSTS header not set. c.Protocol() returns 'HTTP/1.1', not 'https'")
        t.Log("Fix: change c.Protocol() == 'https' to c.Scheme() == 'https' on line 67")
    }
}
```

2. Run: `go test -run Test_PoC_HSTS_NeverSet -v ./middleware/helmet/`

**Expected vulnerable output:**
```
=== RUN   Test_PoC_HSTS_NeverSet
    BUG CONFIRMED: HSTS header not set. c.Protocol() returns 'HTTP/1.1', not 'https'
    Fix: change c.Protocol() == 'https' to c.Scheme() == 'https' on line 67
--- PASS: Test_PoC_HSTS_NeverSet
```

**Expected output after fix:**
```
=== RUN   Test_PoC_HSTS_NeverSet
--- PASS: Test_PoC_HSTS_NeverSet
    (HSTS header is set: "max-age=31536000; includeSubDomains")
```

**Observed output from this environment (commit `ee98695f`):**
```
=== RUN   Test_PoC_HSTS_NeverSet
    poc_hsts_test.go:39: HSTS header value: ""
    poc_hsts_test.go:42: BUG CONFIRMED: HSTS header is NOT set even over TLS
    poc_hsts_test.go:43: Root cause: helmet.go:67 uses c.Protocol() which returns HTTP version
    poc_hsts_test.go:44: c.Protocol() returns 'HTTP/1.1' not 'https'
    poc_hsts_test.go:45: Fix: use c.Scheme() == 'https' instead of c.Protocol() == 'https'
--- PASS: Test_PoC_HSTS_NeverSet
```

**Negative/control case:** With `HSTSMaxAge: 0` (default), HSTS is correctly not set (this is expected behavior, not a bug).

**Cleanup:** Remove `poc_hsts_test.go` after verification.

### Impact

The HSTS header is never applied in production, leaving all users vulnerable to:
- **SSL stripping attacks:** An active network attacker can downgrade HTTPS connections to HTTP, intercepting traffic between the client and server.
- **Protocol downgrade:** Without HSTS, browsers will silently accept HTTP connections to the site, even if the site supports HTTPS.
- **Cookie theft over HTTP:** Session cookies without the `Secure` flag will be sent over HTTP if the user is tricked into an HTTP connection.

This affects any application that:
1. Uses the `helmet` middleware
2. Configures `HSTSMaxAge > 0` expecting HSTS protection
3. Serves traffic over HTTPS

The vulnerability requires an active MITM attacker on the network path, which is realistic in public Wi-Fi, corporate networks, and ISP-level scenarios.

### Suggested remediation

In `middleware/helmet/helmet.go`, line 67, replace `c.Protocol()` with `c.Scheme()`:

```go
// Before (broken):
if c.Protocol() == "https" && cfg.HSTSMaxAge != 0 {

// After (fixed):
if c.Scheme() == "https" && cfg.HSTSMaxAge != 0 {
```

Additionally, update the existing test to use a realistic TLS simulation instead of `SetProtocol("https")`:

```go
// Before (artificial - sets HTTP version to "https" which never happens in practice):
ctx.Request.Header.SetProtocol("https")

// After (realistic - simulates TLS connection):
ctx.RequestCtx().Request.Header.SetProtocol("HTTP/1.1")
ctx.RequestCtx().TLS = &tls.ConnectionState{}
```

**Regression test:** Add a test case that verifies HSTS is set when `req.TLS` is non-nil and `HSTSMaxAge > 0`, without using `SetProtocol`.

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-gv83-gqw6-9j2c
- https://github.com/gofiber/fiber
