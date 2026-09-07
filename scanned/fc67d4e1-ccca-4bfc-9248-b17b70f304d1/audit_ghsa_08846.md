# [M] Nuxt: Reflected XSS in `navigateTo()` external redirect

## Summary
Severity: Medium
Advisory: GHSA-fx6j-w5w5-h468
CVE: CVE-2026-45669
CWE: CWE-83
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-fx6j-w5w5-h468
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=3.4.3 <3.21.6
- npm: `nuxt` — affected >=4.0.0-alpha.1 <4.4.6

## Details
### Summary
`navigateTo()` with `external: true` generates a server-side HTML redirect body containing a `<meta http-equiv="refresh">` tag. The destination URL is only sanitized by replacing `"` with `%22`, leaving `<`, `>`, `&`, and `'` unencoded. An attacker who can influence the URL passed to `navigateTo(url, { external: true })` can break out of the `content="…"` attribute and inject arbitrary HTML/JavaScript that executes under the application's origin.

This is a different root cause from CVE-2024-34343 (GHSA-vf6r-87q4-2vjf), which addressed `javascript:` protocol bypass. The issue here is triggered by any valid URL containing `>`.

### Impact
Applications that pass user-controlled input to `navigateTo(url, { external: true })` — typically via a `?next=` / `?redirect=` query parameter used for post-login or "return to" flows — are vulnerable to reflected cross-site scripting. The injected script runs in the context of the application's origin during the server-rendered redirect response, before the meta-refresh fires.

### Details
In `packages/nuxt/src/app/composables/router.ts`, the SSR redirect path builds an HTML response body with only `"` percent-encoded in the destination URL:

```ts
const encodedLoc = location.replace(/"/g, '%22')
nuxtApp.ssrContext!['~renderResponse'] = {
status: sanitizeStatusCode(options?.redirectCode || 302, 302),
body: `<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=${encodedLoc}"></head></html>`,
headers: { location: encodeURL(location, isExternalHost) },
}
```

The `Location` header is normalised through `encodeURL()` (which uses the `URL` constructor and correctly percent-encodes attribute-significant characters). The HTML body uses a narrower sanitiser. That mismatch is the root cause.

### Proof of concept

Global middleware that forwards a query parameter to `navigateTo`:

```ts
// middleware/redirect.global.ts
export default defineNuxtRouteMiddleware((to) => {
const next = to.query.next as string | undefined
if (next) {
 return navigateTo(next, { external: true })
}
})
```

Request:

```
GET /?next=https://evil.example/x><img src=x onerror=alert(document.domain)>
```

Response body:

```html
<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=https://evil.example/x><img src=x onerror=alert(document.domain)>"></head></html>
```

The `>` after `evil.example/x` terminates the `content="…"` attribute, and the `<img onerror>` tag executes JavaScript in the application's origin before any redirect
occurs.

### Patches
Fixed in `nuxt@4.4.6` and `nuxt@3.21.6` by [#35052](https://github.com/nuxt/nuxt/pull/35052). The fix percent-encodes the full set of HTML-attribute-significant characters (`&`, `"`, `'`, `<`, `>`) before interpolating the URL into the meta-refresh body

### Workarounds
If you can't upgrade immediately, validate user-controlled URLs before passing them to `navigateTo(url, { external: true })`. At minimum, normalise through `new URL(input).toString()` and reject inputs containing `<` or `>` (a normalised URL with these characters is malformed and safe to refuse).

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-fx6j-w5w5-h468
- https://nvd.nist.gov/vuln/detail/CVE-2026-45669
- https://github.com/nuxt/nuxt/pull/35052
- https://github.com/nuxt/nuxt
