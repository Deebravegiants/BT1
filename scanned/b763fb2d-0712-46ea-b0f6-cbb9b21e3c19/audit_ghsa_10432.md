# [M] i18next-locize-backend has URL Injection via Unsanitized Path Parameters

## Summary
Severity: Medium
Advisory: GHSA-mgcp-mfp8-3q45
CVE: CVE-2026-41885
CWE: CWE-22, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-mgcp-mfp8-3q45
Type: github-advisory

## Affected
- npm: `i18next-locize-backend` — affected >=0 <9.0.2

## Details
### Summary

Versions of `i18next-locize-backend` prior to 9.0.2 interpolate `lng`, `ns`, `projectId`, and `version` directly into the configured `loadPath` / `privatePath` / `addPath` / `updatePath` / `getLanguagesPath` URL templates with no path-component validation and no encoding. When an application exposes any of these values to user-controlled input (`?lng=` / `?ns=` query parameters via `i18next-browser-languagedetector`, cookies, request headers, or a URL-derived `projectId`), a crafted value can change the structure of the outgoing request URL.

Affected call sites in `lib/index.js` (pre-patch): the `interpolate()` helper is used at the five URL-build sites — `_readAny`/`read` (line 415 for private, 426 for public), `getLanguages` (lines 271 and 296), and `writePage` (lines 616 and 622) for the missing-key and update POST paths. The helper `interpolate` in `lib/utils.js` substitutes raw values with no encoding.

### Impact

An attacker who can influence `lng`, `ns`, `projectId`, or `version` can:

- **Path traversal** — `lng = '../../admin'` against `https://api.locize.app/{{projectId}}/{{version}}/{{lng}}/{{ns}}` changes the request URL path segment that reaches the locize CDN / API.
- **Query-string injection** — `lng = 'en?x=y'` appends an attacker-chosen query to the URL.
- **Fragment truncation** — `lng = 'en#x'` silently truncates the path in browser fetches.
- **URL-encoded bypass** — `lng = 'en%2F..'` leverages server-side decoding to reintroduce `/..`.

The worst-case concrete impact is loading an unintended translation resource (potentially causing wrong content to render) and, when a custom `loadPath` is configured against an internal / file-scheme URL, **SSRF or arbitrary-file read** on the host running the backend.

Additionally, the pre-patch `interpolate()` function read `data[key]` without excluding prototype-chain properties — under prototype-pollution conditions in the same process, that path could pull values from `Object.prototype` into the URL.

### Related fixes shipped in 9.0.2

- The `defaults()` helper replaces `for...in` iteration with `Object.keys()` plus an explicit prototype-key guard so a polluted `Object.prototype` cannot leak into the merged options object.
- New `utils.interpolateUrl` / `isSafeUrlSegment` / `sanitizeLogValue` / `redactUrlCredentials` helpers mirror the pattern shipped in `i18next-http-backend@3.0.5` (see its advisory [GHSA-q89c-q3h5-w34g](https://github.com/i18next/i18next-http-backend/security/advisories/GHSA-q89c-q3h5-w34g)).

### Affected versions

All versions of `i18next-locize-backend` prior to **9.0.2**.

### Patch

Fixed in **9.0.2**. `lib/index.js` now uses `interpolateUrl()` at every URL-build site and returns an error callback (or silently drops the queued write for `writePage`) when any interpolated value fails the safety check. Legitimate i18next language-code shapes (BCP-47, `en_US`, `zh-Hant-HK`, `my-custom.ns`, `+`-joined multi-language values) all pass.

### Workarounds

No workaround short of upgrading. If you cannot upgrade immediately, sanitise `lng` / `ns` / `projectId` / `version` at your application boundary before passing them through to i18next — reject values containing `..`, `/`, `\`, `?`, `#`, `%`, whitespace, control characters, and cap the length.

### Credits

Discovered via an internal security audit of the i18next / locize ecosystem.

### References

- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [CWE-74: Injection](https://cwe.mitre.org/data/definitions/74.html)
- [CWE-1321: Prototype Pollution (amplification path)](https://cwe.mitre.org/data/definitions/1321.html)
- Related advisory in the same ecosystem: [GHSA-q89c-q3h5-w34g (i18next-http-backend)](https://github.com/i18next/i18next-http-backend/security/advisories/GHSA-q89c-q3h5-w34g)

## References
- https://github.com/locize/i18next-locize-backend/security/advisories/GHSA-mgcp-mfp8-3q45
- https://nvd.nist.gov/vuln/detail/CVE-2026-41885
- https://github.com/locize/i18next-locize-backend/commit/8f81ad4707aa0e90647fde4da5fbe5b23153c6e1
- https://github.com/locize/i18next-locize-backend
- https://github.com/locize/i18next-locize-backend/releases/tag/v9.0.2
