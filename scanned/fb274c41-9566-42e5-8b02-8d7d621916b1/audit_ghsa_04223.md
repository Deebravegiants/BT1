# [M] Nuxt: URL-handling weaknesses in `navigateTo` and `reloadNuxtApp`: SSR open redirect, client-side script execution via the `open` option, and protocol-relative bypass in `reloadNuxtApp`

## Summary
Severity: Medium
Advisory: GHSA-c9cv-mq2m-ppp3
CVE: CVE-2026-56326
CWE: CWE-601, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-c9cv-mq2m-ppp3
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.4.7
- npm: `nuxt` — affected >=3.5.0 <3.21.7

## Details
### Summary

Three weaknesses in Nuxt's client-navigation URL handling, all reachable
from documented public APIs (`navigateTo` and `reloadNuxtApp`):

1. **SSR open redirect in `navigateTo` via path-normalisation bypass.**
   `navigateTo` decided whether a target was external by inspecting the raw
   input with `hasProtocol(..., { acceptRelative: true })`. Inputs such as
   `/..//evil.com`, `/.//evil.com`, `/%2e%2e//evil.com`, or
   `/app/..//evil.com` slipped past that check because they start with
   `/`, but WHATWG URL parsing then normalised them to the
   protocol-relative pathname `//evil.com`. The normalised value was
   written to the `Location` response header and into the
   `<meta http-equiv="refresh">` body of the SSR redirect page, so a
   victim's browser would resolve the redirect cross-origin to the
   attacker's host.

2. **Client-side script execution via `navigateTo({ open: ... })`.** The
   client-side early-open handler called `window.open(toPath, ...)` without
   applying the `isScriptProtocol` check that gates the normal `navigateTo`
   path. A target of `javascript:...` (or another script-capable scheme)
   passed to `navigateTo(url, { open: { ... } })` therefore executed in the
   application's origin instead of being rejected.

3. **Open redirect in `reloadNuxtApp` via protocol-relative bypass.**
   `reloadNuxtApp({ path })` rejects script-capable protocols by parsing
   the path with `new URL(path, window.location.href)` and checking the
   resolved `protocol` against `isScriptProtocol`. Protocol-relative paths
   such as `//evil.com` resolve to the current page's protocol (`https:`),
   which passes that check; the value is then assigned to
   `window.location.href`, which the browser treats as a cross-origin
   redirect. This is the same protocol-relative bypass family as (1), in
   a different sink.

### Impact

For (1), the practical risk is phishing or OAuth-code theft against any
Nuxt app that forwards user-controlled input (for example a `?next=`
query parameter on a login route) into `navigateTo` on the server. The
framework documents that `navigateTo` blocks external hosts unless
`external: true` is passed, so maintainers commonly rely on it as the
safe path for post-login redirects.

For (2), any app that passes a user-controlled URL into
`navigateTo(url, { open: { ... } })` was vulnerable to reflected XSS in
the application's first-party origin.

For (3), any app that forwards user-controlled input into
`reloadNuxtApp({ path })` could be redirected cross-origin for phishing
or OAuth-code theft, even on releases that already shipped the
`isScriptProtocol` guard added by [#35115](https://github.com/nuxt/nuxt/pull/35115).

### Patches

Fixed in `nuxt@4.4.7` and backported to `nuxt@3.21.7`. The three sinks
are addressed by:

- Path-normalisation bypass in `navigateTo`:
  - 4.x: commit [`2cce6fb0`](https://github.com/nuxt/nuxt/commit/2cce6fb02e621196d56df92e05594e07469b5a6d)
  - 3.x: commit [`1f2dd5e7`](https://github.com/nuxt/nuxt/commit/1f2dd5e78c77576437138e97671965573c232835)
- `navigateTo({ open })` script-protocol guard:
  - 4.x: [#35206](https://github.com/nuxt/nuxt/pull/35206) (commit [`3394716d`](https://github.com/nuxt/nuxt/commit/3394716d4a913cba904b028df5338f2aead50032))
  - 3.x: commit [`62fc32ed`](https://github.com/nuxt/nuxt/commit/62fc32eddf648b00a3890141e0235d2a222b024d)
- Protocol-relative bypass in `reloadNuxtApp`:
  - 4.x: commit [`e447a793`](https://github.com/nuxt/nuxt/commit/e447a793c47766834f7497f8412a76cd56fd8ee1)
  - 3.x: commit [`6497d99d`](https://github.com/nuxt/nuxt/commit/6497d99dd106254abd089f6a263d7773869a343b)

### Workarounds

- For (1): validate redirect targets before passing them to `navigateTo`,
  for example reject any input where
  `new URL(target, 'http://localhost').pathname` starts with `//`, or
  only accept a known allow-list of paths.
- For (2): reject any user-controlled URL whose protocol is not in an
  allow-list (typically just `http:` and `https:`) before passing it to
  `navigateTo({ open: ... })`.
- For (3): same shape as (1). Reject paths starting with `//` (or where
  `new URL(path, window.location.href).host !== window.location.host`)
  before passing to `reloadNuxtApp({ path })`.

### References

- CWE-601: URL Redirection to Untrusted Site ('Open Redirect')
- CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')

### Credits

Reported by Anthropic / Claude as `ANT-2026-S08HN6DH` through Anthropic's
coordinated vulnerability disclosure programme.

The `reloadNuxtApp` protocol-relative bypass (sink 3) was independently
reported by [@alcls01111](https://github.com/alcls01111) via GitHub's
coordinated disclosure flow (`GHSA-w7fp-2cfv-4837`), closed as a
duplicate of this advisory.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-c9cv-mq2m-ppp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-56326
- https://github.com/nuxt/nuxt/pull/35115
- https://github.com/nuxt/nuxt/pull/35206
- https://github.com/nuxt/nuxt/commit/1f2dd5e78c77576437138e97671965573c232835
- https://github.com/nuxt/nuxt/commit/2cce6fb02e621196d56df92e05594e07469b5a6d
- https://github.com/nuxt/nuxt/commit/3394716d4a913cba904b028df5338f2aead50032
- https://github.com/nuxt/nuxt/commit/62fc32eddf648b00a3890141e0235d2a222b024d
- https://github.com/nuxt/nuxt/commit/6497d99dd106254abd089f6a263d7773869a343b
- https://github.com/nuxt/nuxt/commit/e447a793c47766834f7497f8412a76cd56fd8ee1
- https://github.com/nuxt/nuxt
- https://www.vulncheck.com/advisories/nuxt-server-side-open-redirect-via-path-normalization-bypass-in-navigateto
