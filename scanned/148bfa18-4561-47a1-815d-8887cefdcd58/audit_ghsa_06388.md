# [M] Appium: Reflected XSS / arbitrary JS in @appium/base-driver /test/guinea-pig* routes

## Summary
Severity: Medium
Advisory: GHSA-3wgp-x9p5-c7cc
CVE: CVE-2026-58191
CWE: CWE-489, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-3wgp-x9p5-c7cc
Type: github-advisory

## Affected
- npm: `@appium/base-driver` — affected >=0 <10.7.0

## Details
## Summary

Appium's base-driver mounts the built-in `/test/guinea-pig`, `/test/guinea-pig-scrollable` and `/test/guinea-pig-app-banner` routes **unconditionally** on every server. The handler reflects the `throwError` query param, the `comments` POST field, and the `User-Agent` request header into the returned HTML via `compileLodashTemplate`, which interpolates `<%= expr %>` as `String(expr)` with **no HTML/JS escaping**. This yields reflected XSS, and the `throwError` value is reflected **inside a `<script>` block**, giving arbitrary JavaScript execution on the server's origin. No authentication, no session, no driver and no plugin are required, and the default bind address is `0.0.0.0`.

## Details

### Affected
- `@appium/base-driver` **10.6.0** (with Appium server **3.5.0**); tested live.
- Template engine helper: `@appium/base-driver` `lib/utils.ts` `compileLodashTemplate`.

### Location (file:line)
- Routes mounted unconditionally: `base-driver/lib/express/server.ts:216-219`
(`app.all('/test/guinea-pig', guineaPig)` etc.).
- Tainting: `base-driver/lib/express/static.ts:35-61` (`guineaPigTemplate`) —
`throwError = String(req.params.throwError ?? req.query?.throwError)`, `params.comment = String(req.body.comments)`, `params.userAgent = req.headers['user-agent']`.
- Unescaped render: `base-driver/lib/utils.ts:67-83` (`compileLodashTemplate`)
emits `<%= expr %>` as `String(${expr})` via `new Function(...)`, no escaping.
- Sinks (shipped templates): `base-driver/static/test/guinea-pig.html:11-12`
(`throwError` inside `<script>`), `:50` (`comment`), `:87` (`userAgent`); same in `guinea-pig-scrollable.html` / `guinea-pig-app-banner.html`.


### PoC

Requests:
```
GET /test/guinea-pig?throwError=x%27%2balert(document.domain)%2b%27
POST /test/guinea-pig         (body: comments=</span><img src=x onerror=alert(1)>)
GET  /test/guinea-pig         (header: User-Agent: <script>alert(7)</script>)
```

<img width="973" height="276" alt="image" src="https://github.com/user-attachments/assets/f58e1dce-f3ad-43d3-b66e-1ff5efea3866" />


### Impact

An attacker who can get a victim to open a crafted link (or auto-submit a form) to the Appium server executes arbitrary JavaScript on the server's origin. With default CORS `*` + no authentication, that JS can drive the WebDriver REST API and plugin endpoints. The endpoints are debug/test fixtures that should not be reachable on a production listener at all.

## References
- https://github.com/appium/appium/security/advisories/GHSA-3wgp-x9p5-c7cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-58191
- https://github.com/appium/appium/pull/22394
- https://github.com/appium/appium/commit/d94a40af9f8040191ee7888571a1c9d5aec59f89
- https://github.com/appium/appium
- https://github.com/appium/appium/releases/tag/@appium/base-driver@10.7.0
