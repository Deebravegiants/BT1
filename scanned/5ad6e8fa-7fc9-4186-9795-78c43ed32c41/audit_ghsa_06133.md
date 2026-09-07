# [M] Mailpit: WebSocket origin check bypass via percent-encoded path (regression of CVE-2026-22689)

## Summary
Severity: Medium
Advisory: GHSA-8r62-w5wh-fc5m
CVE: CVE-2026-67448
CWE: CWE-177, CWE-200, CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8r62-w5wh-fc5m
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=1.29.0 <1.30.6

## Details
## Summary

The cross-site WebSocket hijacking fix was reimplemented as an origin check gated on a raw-URI prefix test, but Go's ServeMux routes on the percent-decoded path, so requesting /%61pi/events reaches the WebSocket handler while skipping the only origin control, and the upgrader itself accepts every origin. Confirmed at HEAD 408b30d. Affects 1.29.0 through 1.30.5.

## The defect

Two halves that were each correct in isolation. server/websockets/client.go accepts any origin and delegates the check elsewhere:

```go
var upgrader = websocket.Upgrader{                       // line 33
    ...
    CheckOrigin: func(_ *http.Request) bool {            // line 37
        // origin is checked via server.go's CORS settings
        return true                                      // line 39
    },
}
```

server/server.go performs that check but keys it on the RAW request target:

```go
if strings.HasPrefix(r.RequestURI, config.Webroot+"api/") || htmlPreviewRouteRe.MatchString(r.RequestURI) {   // line 320
    if allowed := corsOriginAccessControl(r); !allowed {
        http.Error(w, "Blocked due to CORS violation", http.StatusForbidden)
        return
    }
```

r.RequestURI is the untouched wire target; Go's ServeMux routes on the percent-DECODED path. So for /%61pi/events: `strings.HasPrefix("/%61pi/events", "/api/")` is FALSE (origin check skipped), ServeMux decodes %61 to "a" and routes to /api/events, and the upgrader's CheckOrigin returns true.

Measured, default config, no auth: /api/events with `Origin: https://evil.example` returns 403; /%61pi/events with the same Origin returns 101 Switching Protocols and begins streaming. With a message delivered over SMTP while the cross-origin socket was open, the attacker origin received the ID, Message-Id, From, To, Cc, Bcc, Subject ("SECRET password reset token abc123"), size, tags, and body Snippet, live. WebSockets are not subject to CORS response-header enforcement, so the absent Access-Control-Allow-Origin header provides no protection once the upgrade succeeds.

Regression provenance: commit 6f1f4f3 (2026-01-10, v1.28.2) fixed CVE-2026-22689 by DELETING CheckOrigin; commit a63bcd9 (2026-01-31, first in v1.29.0) reintroduced CheckOrigin returning true and replaced the protection with the bypassable raw-prefix test.

## Attacker model and verification

Any website the developer visits while Mailpit is running. No credentials, no ability to send mail, no interaction beyond visiting a page. Requires Mailpit without --ui-auth-file (the default, and the same precondition as the original CVE). The bypass was measured live against a real Mailpit instance on loopback, including the 403-versus-101 control pair; authentication still holds (the encoded path returns 401 when --ui-auth-file is set); browser reachability was confirmed against the WHATWG URL parser, which preserves %61.

## Suggested fix

Do not make security decisions on r.RequestURI. Key the check on r.URL.Path, the decoded value the router uses, so the gate and the route agree. Better, restore a real CheckOrigin on the upgrader so the WebSocket carries its own origin enforcement rather than depending on a middleware prefix match. Secondary (Low, not claimed as XSS): server/apiv1/message.go lines 154-155 echo an attacker-chosen Content-Type with Content-Disposition: inline; this is blocked today by the nonce CSP.

## Tooling

I used AI assistance while investigating. The bypass was measured live against a real Mailpit instance on loopback, including the 403-versus-101 control pair and the authenticated 401 case, and I separately confirmed at HEAD the CheckOrigin returning true with its delegating comment and the RequestURI-keyed prefix gate.

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-8r62-w5wh-fc5m
- https://github.com/axllent/mailpit/commit/fbe5e006c3f1682b819df58b4a932d7a84920be9
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.30.6
