# [M] PinchTab: API Bearer Token Exposed in URL Query Parameter via Server Logs and Intermediary Systems

## Summary
Severity: Medium
Advisory: GHSA-mrqc-3276-74f8
CVE: CVE-2026-33620
CWE: CWE-598
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-mrqc-3276-74f8
Type: github-advisory

## Affected
- Go: `github.com/pinchtab/pinchtab` — affected >=0.7.8 <0.8.4

## Details
### Summary
PinchTab `v0.7.8` through `v0.8.3` accepted the API token from a `token` URL query parameter in addition to the `Authorization` header. When a valid API credential is sent in the URL, it can be exposed through request URIs recorded by intermediaries or client-side tooling, such as reverse proxy access logs, browser history, shell history, clipboard history, and tracing systems that capture full URLs.

This issue is an unsafe credential transport pattern rather than a direct authentication bypass. It only affects deployments where a token is configured and a client actually uses the query-parameter form. PinchTab's security guidance already recommended `Authorization: Bearer <token>`, but `v0.8.3` still accepted `?token=` and included first-party flows that generated and consumed URLs containing the token.

This was addressed in v0.8.4 by removing query-string token authentication and requiring safer header- or session-based authentication flows.

### Details
**Issue 1 — Query-string token accepted in `v0.7.8` through `v0.8.3` (`internal/handlers/middleware.go`):**
The `v0.8.3` authentication middleware accepted credentials from the URL query string:

```
// internal/handlers/middleware.go — v0.8.3
auth := r.Header.Get("Authorization")
qToken := r.URL.Query().Get("token")

if auth == "" && qToken == "" {
    web.ErrorCode(w, 401, "missing_token", "unauthorized", false, nil)
    return
}

provided := strings.TrimPrefix(auth, "Bearer ")
if provided == auth {
    if qToken != "" {
        provided = qToken
    } else {
        provided = auth
    }
}

if subtle.ConstantTimeCompare([]byte(provided), []byte(cfg.Token)) != 1 {
    web.ErrorCode(w, 401, "bad_token", "unauthorized", false, nil)
    return
}
```

This means any client sending `GET /health?token=<secret>` in `v0.8.3` would authenticate successfully without using the `Authorization` header. I verified the same query-token auth pattern is present in the historical tag range starting at `v0.7.8`, and it is removed in `v0.8.4`.

**Issue 2 — First-party setup and dashboard flows in `v0.8.3` generated and consumed `?token=` URLs:**
The `v0.8.3` setup flow generated dashboard URLs containing the token in the query string:

```
// cmd/pinchtab/cmd_wizard.go — v0.8.3
func dashboardURL(cfg *config.FileConfig, path string) string {
    host := orDefault(cfg.Server.Bind, "127.0.0.1")
    port := orDefault(cfg.Server.Port, "9867")
    url := fmt.Sprintf("http://%s:%s%s", host, port, path)
    if cfg.Server.Token != "" {
        url += "?token=" + cfg.Server.Token
    }
    return url
}
```

The `v0.8.3` dashboard frontend also supported one-click login from that same query-string token:

```
// dashboard/src/App.tsx — v0.8.3
const params = new URLSearchParams(window.location.search);
const urlToken = params.get("token");
if (urlToken) {
    setStoredAuthToken(urlToken);
    clean.searchParams.delete("token");
    window.history.replaceState({}, "", clean.pathname + clean.hash);
    window.location.reload();
}
```

That combination materially increased the chance that users would open, copy, paste, bookmark, or log URLs containing live credentials before the token was scrubbed from the visible address bar.

**Issue 3 — Exposure depends on surrounding systems recording the URL:**
PinchTab's own request logger records `r.URL.Path`, not the full raw query string, so the leak is not primarily through PinchTab's structured application log. The risk comes from surrounding systems or client tooling that record the full request URI, such as:

1. reverse proxies and load balancers
2. browser history or bookmarks
3. shell history containing full `curl` commands
4. clipboard or terminal history when the wizard prints and copies a tokenized URL
5. tracing or monitoring systems that capture full request URLs

### PoC
**Step 1 — Confirm auth is required**

```bash
curl -i http://localhost:9867/health
```

Expected in token-protected affected deployments:

```http
HTTP/1.1 401 Unauthorized
```

**Step 2 — Authenticate using the vulnerable query-parameter pattern**

```bash
curl -i "http://localhost:9867/health?token=supersecrettoken"
```

Expected:

```http
HTTP/1.1 200 OK
```

This demonstrates that the token is accepted from the URL.

**Step 3 — Observe the exposure vector**
If the request traverses a system that records the full URI, the token may appear in logs or local history, for example:

```text
GET /health?token=supersecrettoken HTTP/1.1
```

In `v0.8.3`, a first-party reproduction path also exists without any external proxy: run the setup wizard, copy the printed dashboard URL containing `?token=...`, and note that the live credential is now present in clipboard history and any place that URL is pasted.

### Impact
1. Exposure of a valid API token through unsafe URL-based transport when a client uses the `?token=` authentication form.
2. Lower barrier for credential compromise where reverse proxies, browser history, shell history, clipboard history, or tracing systems retain full request URIs.
3. The `v0.8.3` wizard/dashboard flow increased the practical likelihood of this exposure by generating and consuming tokenized URLs as a first-party login pattern.
4. Practical risk depends on actual use of the query-token pattern; deployments that use only `Authorization: Bearer <token>` are not affected by this issue in practice.
5. This is not a direct authentication bypass. An attacker still needs access to a secondary source that captured the URL containing the token.

### Suggested Remediation
1. Reject query-string token authentication and accept credentials only through the `Authorization` header or controlled session mechanisms.
2. Avoid generating user-facing URLs that contain live credentials.
3. Document header-based auth as the only supported non-browser API authentication pattern.
4. Recommend token rotation for users who may previously have used query-parameter authentication.

**Screenshot Capture**
<img width="1162" height="164" alt="ภาพถ่ายหน้าจอ 2569-03-18 เวลา 12 46 08" src="https://github.com/user-attachments/assets/e68b4469-dafd-400d-a6e1-f74d368cc8ac" />

## References
- https://github.com/pinchtab/pinchtab/security/advisories/GHSA-mrqc-3276-74f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33620
- https://github.com/pinchtab/pinchtab
- https://github.com/pinchtab/pinchtab/releases/tag/v0.8.4
