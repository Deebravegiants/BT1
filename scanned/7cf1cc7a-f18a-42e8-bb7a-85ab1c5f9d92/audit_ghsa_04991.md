# [H] nebula-mesh's web UI lacks CSRF tokens on /ui/* mutating endpoints

## Summary
Severity: High
Advisory: GHSA-273q-qgh5-wrj6
CVE: CVE-2026-47725
CWE: CWE-269, CWE-352
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-273q-qgh5-wrj6
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.3

## Details
Every `/ui/*` POST / PUT / PATCH / DELETE route processes the request as soon as the session cookie validates. `SameSite=Lax` on the session cookie prevents most cross-site form submits but does not protect:

- top-level form-submit navigations from third-party pages (some browsers still send Lax cookies on top-level POSTs)
- same-registrable-domain attackers (sibling-subdomain XSS, subdomain takeover)
- the `GET /ui/logout` route, which a third-party `<img src=".../ui/logout">` can force-trigger

The admin UI signs CA certificates, mints API keys, rotates / retires / deletes CAs, disables operators, and changes server settings. CSRF here is a real privilege escalation, not just annoyance.

## Affected
All released versions up to v0.3.2.

## Suggested fix
Double-submit cookie: a 32-byte `crypto/rand` token in a non-HttpOnly `_csrf` cookie, echoed in either `X-CSRF-Token` (htmx) or a `_csrf` form field (HTML forms). Compared in constant time. Rotated on every privilege transition (`Login`, OIDC `StartAuthenticatedSession`, `CompleteTwoFactor`, `Logout`) so pre-auth fixation cannot survive promotion. Rejections audit-logged as `ui.csrf.rejected` with reason; response body stays opaque.

`/ui/logout` becomes POST so it is no longer reachable via `<img>` tags.

Fix coordinates with the Secure-cookie advisory disclosed concurrently — the `_csrf` cookie inherits the same `Secure`-attribute derivation.

## Reproducer
With an authenticated operator session in browser tab A, open the following minimal HTML in any other tab:

```html
<form action="https://nebula.example.com/ui/cas/{ca-id}/delete" method="POST">
  <button>Click for free puppy</button>
</form>
```

Click. The CA is deleted — the server processes the POST because the session cookie is automatically attached and there is no other check. The same trick works for force-rotate, retire, mint API keys, disable operators, etc.

Alternative force-logout: `<img src="https://nebula.example.com/ui/logout">` placed on an attacker's page logs out any visiting authenticated operator. No interaction required.

## Notes
- Multipart and JSON endpoints don't exist in the current UI surface. Future additions must rely on the header path because `r.PostFormValue` only reads `application/x-www-form-urlencoded` bodies. The middleware's package comment documents this.
- The patch assumes nebula-mgmt is the sole authority on its registrable domain. A compromised sibling subdomain can still set parent-domain cookies and forge matches; SameSite=Lax does not prevent that. Documented in the patch.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-273q-qgh5-wrj6
- https://github.com/juev/nebula-mesh
