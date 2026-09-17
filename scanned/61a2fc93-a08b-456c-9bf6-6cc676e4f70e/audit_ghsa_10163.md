# [M]  i18next-http-backend has Path Traversal & URL Injection via Unsanitised lng/ns

## Summary
Severity: Medium
Advisory: GHSA-q89c-q3h5-w34g
CVE: CVE-2026-41691
CWE: CWE-22, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-q89c-q3h5-w34g
Type: github-advisory

## Affected
- npm: `i18next-http-backend` — affected >=0 <3.0.5

## Details
### Summary

Versions of `i18next-http-backend` prior to 3.0.5 interpolate the `lng` and `ns` values directly into the configured `loadPath` / `addPath` URL template without any encoding, validation, or path sanitisation. When an application exposes the language-code selection to user-controlled input (the default — `i18next-browser-languagedetector` reads `?lng=` query params, cookies, `localStorage`, and request headers), an attacker can inject characters that change the structure of the outgoing request URL.

Affected call sites:

- `_readAny` — `lib/index.js:64`: `interpolate(resolvedLoadPath, { lng: languages.join('+'), ns: namespaces.join('+') })`
- `create` — `lib/index.js:123` (pre-patch): `interpolate(addPath, { lng, ns: namespace })`

The helper `interpolate` (`lib/utils.js`) previously returned the raw value with no encoding. In contrast, `addQueryString` already correctly uses `encodeURIComponent` for each query-string param — only the URL-path substitution was unprotected.

### Impact

An attacker who can influence the resolved `lng` or `ns` value can alter the URL in several ways:

- **Path traversal** — `lng = '../../config'` turns `/locales/{{lng}}/{{ns}}.json` into `/locales/../../config/translation.json`. On a misconfigured web server, this can cause the request to target a different resource than intended; in SSR pipelines that use `file://` or similar schemes for `loadPath`, it can read arbitrary files from the host filesystem.
- **Query-string injection** — `lng = 'en?admin=true'` turns `/locales/{{lng}}/{{ns}}.json` into `/locales/en?admin=true/translation.json`. Some server frameworks parse the query portion with higher priority than the path and branch on attacker-controlled flags.
- **Fragment truncation** — `lng = 'en#anything'` silently discards the rest of the path in browser fetches (client cannot see the final URL).
- **URL-encoded bypasses** — `lng = 'en%2F..'`, after server-side URL decoding, resolves to `en/..` — the attacker bypasses the absence of a literal `/` in their input.

The practical worst case is **SSRF** when `loadPath` is an internal or file-scheme URL, and **path-based authorisation bypass** against servers that segment access by URL prefix.

### Also fixed in 3.0.5

- **Per-instance `omitFetchOptions`.** A module-level boolean in `lib/request.js` was flipped to `true` the first time any backend instance hit a "not implemented" fetch error. Once flipped, **all** subsequent requests from **all** backend instances in the same module silently stripped every user-configured fetch option — including security-relevant `credentials`, `mode`, and `cache`. One misbehaving instance (for example during SSR hydration or in React Native) permanently removed these protections process-wide. 3.0.5 scopes the flag to the backend's `options` object (`options._omitFetchOptions`) so one instance's fallback cannot pollute siblings.
- **Log forging via control characters in `lng`/`ns`.** Error callbacks embedded the raw `lng`/`ns`/URL in the message string. Crafted CR/LF values could inject fake log lines into file-backed log aggregators (CWE-117). 3.0.5 strips C0/C1 control chars before concatenation.
- **Basic-auth credentials leaked into error callbacks.** If `loadPath` contained a `user:password@host` authority, the full URL (including the credentials) ended up in the error message strings returned to the caller. 3.0.5 redacts `user:password@` before logging.
- **Prototype-pollution amplification via `for...in`.** `addQueryString` and the XHR `customHeaders` loop used `for...in` which walks the prototype chain. Polluted `Object.prototype` entries could leak into URL query parameters and request headers. 3.0.5 uses `Object.keys` and an explicit prototype-key guard.

### Affected versions

All versions of `i18next-http-backend` prior to **3.0.5**.

### Patch

Fixed in **3.0.5**. Summary of the hardening:

1. New `utils.interpolateUrl` (used by `_readAny` and `create`) returns `null` if any substitution fails the URL-segment safety check (blocks `..`, `/`, `\`, `?`, `#`, `%`, `@`, whitespace, control chars, prototype keys, and values > 128 chars). Multi-language joins (`en+de`) are validated per-segment. The call sites now refuse to issue a request when the check fails and call back with a clear error.
2. `omitFetchOptions` is stored per-instance on `options._omitFetchOptions`.
3. Error-callback messages sanitise strings and redact URL credentials.
4. `for...in` over untrusted objects replaced with `Object.keys` + prototype-key guard.

### Workarounds

No workaround short of upgrading. If you cannot upgrade immediately, sanitise `lng` / `ns` yourself before they reach i18next (strip `..`, `/`, `\`, `?`, `#`, `%`, whitespace, and control characters; cap the length).

### Credits

Discovered via an internal security audit of the i18next ecosystem.

## References
- https://github.com/i18next/i18next-http-backend/security/advisories/GHSA-q89c-q3h5-w34g
- https://nvd.nist.gov/vuln/detail/CVE-2026-41691
- https://github.com/i18next/i18next-http-backend/commit/4cee84f229c637b9c182366d3156f726d407a621
- https://github.com/i18next/i18next-http-backend
