# [M] i18nextify has DOM XSS via javascript:/data: URL schemes in translated href/src attributes

## Summary
Severity: Medium
Advisory: GHSA-6457-mxpq-4fqq
CVE: CVE-2026-41692
CWE: CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-6457-mxpq-4fqq
Type: github-advisory

## Affected
- npm: `i18nextify` — affected >=0 <4.0.8

## Details
### Summary

Versions of `i18nextify` prior to 4.0.8 substitute `{{key}}` interpolation tokens inside `src` and `href` attribute values with the raw string returned by `i18next.t()`. The substitution logic in `src/localize.js` (`replaceInside` handler around line 122) only guards against a duplicated `http://` origin prefix — it does not validate the URL scheme of the substituted value. A translated value such as `javascript:alert(1)` or `data:text/html,<script>...</script>` is applied unchanged to the live DOM attribute.

### Impact

When an attacker can influence the content of a translation file or the translation-backend response — compromised translation CDN, user-contributed locales, MITM on a plain-HTTP backend, write access to the translation JSON — they can:

- Set any `href` on an anchor to a `javascript:` URI, executing arbitrary JavaScript when the victim clicks the link.
- Set any `src` on `<iframe>`, `<object>`, or `<embed>` to a `data:text/html` URI containing a full script payload that runs in the page's origin.
- Use `vbscript:` on legacy IE installations or `file:` for local-resource navigation attacks.

This path is distinct from the general i18nextify design that intentionally renders HTML from translations — href/src schemes are narrow and attack-specific, and no legitimate translation needs `javascript:` or `data:`. The fix therefore blocks these schemes outright without changing other behaviour.

### Also fixed in 4.0.8

- **`debug` / `saveMissing` URL-parameter substring match.** The previous detection `window.location.search.indexOf('debug=true') > -1` matched the substring anywhere in the query string. A URL like `?nosaveMissing=true` silently enabled `saveMissing` mode, causing the victim's browser to POST every unknown translation key to the configured `addPath` — a form of CSRF-style abuse of missing-key reporting. `?track_debug=true` enabled verbose debug logging, leaking i18next internals to the console. Now uses `URLSearchParams` for exact parameter matching.
- **Optional `sanitize(html, ctx)` hook.** The library's core purpose is to render HTML from translations — a behaviour that is safe only when the translation source is fully trusted. Applications with partially-trusted sources (user-contributed locales, third-party CDN, MITM-exposed HTTP backend) can now wire a sanitizer (e.g. DOMPurify) via `i18next.options.sanitize`. Defaults to pass-through to preserve existing behaviour for the main use case.

### Affected versions

All versions of `i18nextify` prior to **4.0.8**.

### Patch

Fixed in **4.0.8**. The URL-scheme blocklist is `^\s*(javascript|data|vbscript|file)\s*:` (case-insensitive) applied to each translated value before it is joined back into the `href`/`src` attribute. Values matching the blocklist are replaced with an empty string so the attribute becomes harmless rather than leaving the attacker's URL in place.

### Workarounds

No workaround short of upgrading. If you cannot upgrade immediately, audit every translation file for `javascript:`, `data:`, `vbscript:`, and `file:` prefixes in any value that may reach an `href`/`src` position, and restrict translation-file write access to trusted operators. Serving translations over HTTPS and pinning the translation backend to an internal origin reduce the MITM surface.

### Credits

Discovered via an internal security audit of the i18next ecosystem.

## References
- https://github.com/i18next/i18nextify/security/advisories/GHSA-6457-mxpq-4fqq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41692
- https://github.com/i18next/i18nextify/commit/16f23dbcdcf893673587f7a03355bf7ce0a0e49e
- https://github.com/i18next/i18nextify
