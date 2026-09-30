# [M] Nuxt: Reflected XSS in `<NuxtLink>` via unsanitised `javascript:` or `data:` URL

## Summary
Severity: Medium
Advisory: GHSA-934w-87qh-qr26
CVE: CVE-2026-53722
CWE: CWE-79, CWE-83
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-934w-87qh-qr26
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.4.7
- npm: `nuxt` — affected >=3.0.0 <3.21.7

## Details
### Summary

`<NuxtLink>` did not validate the URL scheme of values bound to its `to` or `href` props before rendering them into the `href` attribute of the underlying `<a>` element. When an application binds attacker-controlled input (a query parameter, a CMS field, a user-supplied profile URL) to `<NuxtLink :to>` or `:href`, the attacker can supply a `javascript:` or `vbscript:` URL that is reflected verbatim into the rendered markup. Clicking the link executes the supplied script in the origin of the Nuxt application, resulting in reflected DOM-based cross-site scripting. A `data:text/html,...` payload reflected through the same sink does not execute in the application's origin but enables a same-tab phishing surface anchored to a legitimate application link.

The same value was exposed to consumers of the component's `custom` slot via the `href` and `route.href` props, so applications that re-bind those values to their own anchors were affected identically.

Unlike the previously reported `navigateTo` issue (CVE-2024-34343), the sink here is the rendered anchor itself; the existing `isScriptProtocol` checks in `navigateTo` and `reloadNuxtApp` are not on the code path. The `onClick` handler intentionally returns early for external links so the browser's native protocol-based navigation runs.

### Affected component

- File: `packages/nuxt/src/app/components/nuxt-link.ts`
- Sink: `h('a', { href: href.value, ... })` in the default render, plus the `href` / `route.href` props passed to the `custom` slot.
- Broken check: external auto-detection treated any `hasProtocol(path, { acceptRelative: true })` value as an "external link", then rendered the value directly as `<a href>` without rejecting script-capable protocols. There was no equivalent of the `navigateTo` `isScriptProtocol(protocol)` gate in this path.

### Impact

Any Nuxt application that binds user-controlled values to `<NuxtLink :to>` / `:href` was vulnerable. Common shapes: profile-link rendering (`<NuxtLink :to="user.website">`), "share this" / "open in new tab" handlers that pass through a query parameter, CMS-driven landing pages that render `<NuxtLink :to="cms.cta.url">`, and marketplace listings that show seller-supplied links.

For `javascript:` / `vbscript:` the primitive is reflected XSS in the application's first-party origin (session theft for non-`HttpOnly` cookies, CSRF token theft, account takeover via DOM rewriting, credential harvesting via fake login overlays). For `data:text/html,...` the attacker gets a same-tab phishing surface anchored to a legitimate application link.

### Patches

Fixed in `nuxt@4.4.7` (commit [`0103ce06`](https://github.com/nuxt/nuxt/commit/0103ce06fbbbdfa079a7f020ef8ce00121eac4a3)) and backported to `nuxt@3.21.7` (commit [`53284043`](https://github.com/nuxt/nuxt/commit/53284043dc21210a25d629d1cec67d3ae557ffd0)). The fix sanitises the resolved external `href` before it is passed to `<a>` or the `custom` slot: control characters and whitespace are stripped, leading `view-source:` prefixes are unwrapped, and any remaining script-capable scheme (per `isScriptProtocol`) causes the `href` to be replaced with an empty string.

### Workarounds

Until you can upgrade, validate URLs at the source before binding them to `<NuxtLink :to>` / `:href`. For example, only accept paths that start with `/` (and not `//`), or run user-supplied URLs through `new URL(value)` and reject anything whose `protocol` is not in an allow-list (typically `http:` and `https:`).

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-934w-87qh-qr26
- https://nvd.nist.gov/vuln/detail/CVE-2026-53722
- https://github.com/nuxt/nuxt/commit/0103ce06fbbbdfa079a7f020ef8ce00121eac4a3
- https://github.com/nuxt/nuxt/commit/53284043dc21210a25d629d1cec67d3ae557ffd0
- https://github.com/nuxt/nuxt
