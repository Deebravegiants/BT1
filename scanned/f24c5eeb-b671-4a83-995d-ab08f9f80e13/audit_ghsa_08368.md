# [H] Portainer: JWT accepted in URL query leaks tokens to logs and referers

## Summary
Severity: High
Advisory: GHSA-jvp4-q659-95mj
CVE: CVE-2026-44883
CWE: CWE-598
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-jvp4-q659-95mj
Type: github-advisory

## Affected
- Go: `github.com/portainer/portainer` — affected >=2.33.0 <2.33.8
- Go: `github.com/portainer/portainer` — affected >=2.39.0 <2.39.2
- Go: `github.com/portainer/portainer` — affected >=2.40.0 <2.41.0

## Details
## Summary
Portainer's authentication middleware accepts JWT bearer tokens passed as the `?token=<JWT>` URL query parameter on any authenticated API endpoint, in addition to the standard `Authorization: Bearer` header. URLs are recorded in reverse-proxy access logs, browser history, and HTTP `Referer` headers on outbound navigation, so any JWT passed this way can be harvested by anyone with access to those logs or by an external site the user subsequently visits. A leaked token grants the full privileges of the user it was issued to, until the token expires (default 8 hours, configurable).

The `?token=` parameter was used by Portainer's browser-based container attach, exec, and pod shell features, so any user with exec or attach rights on a container was exposed — not only administrators.

## Severity
**High**

Attack complexity is High because exploitation depends on the attacker obtaining a leaked token from a log, referer, or shared URL. Once obtained, a leaked token grants the privileges of the user it was issued to; for administrator tokens this compromises confidentiality, integrity, and availability of Portainer itself and of every Docker/Kubernetes environment it manages — container exec and stack deployment make host-level compromise reachable, so subsequent-system impact is also High.

## Affected Versions
Query-parameter token acceptance has existed since JWT authentication was introduced in Portainer.

Fixes are included in the following releases:

| Branch              | First vulnerable | Fixed in   |
|---------------------|------------------|------------|
| 2.33.x (LTS)        | 2.33.0           | **2.33.8** |
| 2.39.x (LTS)        | 2.39.0           | **2.39.2** |
| 2.40.x (STS)        | all prior        | **2.41.0** |

Portainer releases prior to 2.33.0 are end-of-life and will not receive a fix. Users on EOL versions should upgrade to a supported LTS branch.

## Workarounds
Administrators who cannot immediately upgrade can reduce exposure by:

- **Stripping `?token=` at the reverse proxy.** A rewrite rule in nginx, Traefik, or equivalent that removes the `token` query parameter before the request reaches Portainer blocks the query-parameter auth path entirely. Container exec and interactive shells rely on the query-parameter token for WebSocket upgrade and will stop working until the patched release is deployed.
- **Auditing existing logs.** Search reverse-proxy access logs and application logs for `?token=` or `&token=` occurrences and treat any captured JWT as compromised. Resetting the affected user's password invalidates their sessions; reducing the JWT session timeout in Portainer settings shortens the exposure window for tokens already issued.
- **Administrator hygiene.** Do not share Portainer URLs that contain `?token=` in chat, email, or tickets, and avoid navigating to external sites from within the Portainer UI on unpatched instances — the `Referer` header will carry the token.

None of these replace the fix.

## Affected Code
Pre-fix, `extractBearerToken` in `api/http/security/bouncer.go` read the JWT from the `token` query parameter before falling back to the `Authorization` header. The `query.Del("token")` call scrubs the parameter from `r.URL.RawQuery` on the way through Portainer, but by that point the original URL has already been recorded by any upstream reverse proxy, access logger, or browser.

```go
func extractBearerToken(r *http.Request) (string, bool) {
    query := r.URL.Query()
    token := query.Get("token")
    if token != "" {
        query.Del("token")
        r.URL.RawQuery = query.Encode()
        return token, true
    }

    tokens, ok := r.Header[jwtTokenHeader]
    if !ok || len(tokens) == 0 {
        return "", false
    }
    // ...
}
```

The fix removes the query-parameter path entirely. Authenticated requests now carry the JWT via the `Authorization` header for API clients, or via the `portainer_api_key` HttpOnly cookie for the browser UI — cookies are sent automatically on same-origin WebSocket upgrade requests, so the browser-based container attach, exec, and pod shell features continue to work without exposing the token in the URL. The WebSocket handlers that previously documented `?token=` as a required query parameter have been updated to match.

## Impact
- **Token leakage to infrastructure.** Intermediate systems that observe the request URL — reverse proxies, load balancers, access logs, WAFs, and corporate network monitoring — capture the full JWT in plaintext.
- **Token leakage via the browser.** URLs containing `?token=` are recorded in browser history and forwarded in the `Referer` header on any outbound navigation from the Portainer UI.
- **Account takeover.** Anyone with access to a leaked JWT acts as the authenticated user for the remainder of the token's validity, without needing the password. If the leaked token belongs to an administrator, the attacker gains full API access including user management, container exec, and stack deployment.
- **Reach beyond Portainer.** Container exec with an administrator JWT reaches the host filesystem of managed environments and can be used to execute commands on those hosts.

## Timeline
- 2026-03-06: Reported via GitHub Security Advisory by **scanpwn**.
- 2026-04-14: Fix merged to `develop`.
- 2026-04-29: 2.41.0 released.
- 2026-05-07: 2.39.2-LTS and 2.33.8-LTS released.

## Credit
- **scanpwn** — identified and reported the query-parameter JWT acceptance and the resulting token-leakage vectors.

## References
- https://github.com/portainer/portainer/security/advisories/GHSA-jvp4-q659-95mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44883
- https://github.com/portainer/portainer
- https://github.com/portainer/portainer/releases/tag/2.33.8
- https://github.com/portainer/portainer/releases/tag/2.39.2
- https://github.com/portainer/portainer/releases/tag/2.41.0
