# [H] i18next-http-middleware: HTTP response splitting and DoS via unsanitised Content-Language header

## Summary
Severity: High
Advisory: GHSA-c3h8-g69v-pjrg
CVE: CVE-2026-41683
CWE: CWE-113, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-c3h8-g69v-pjrg
Type: github-advisory

## Affected
- npm: `i18next-http-middleware` — affected >=0 <3.9.3

## Details
### Summary

Versions of `i18next-http-middleware` prior to 3.9.3 wrote user-controlled language values into the `Content-Language` response header after passing them through `utils.escape()`, which is an HTML-entity encoder that does not strip carriage return, line feed, or other control characters. When the application used an older `i18next` (< 19.5.0) that still exercised the backward-compatibility fallback at `LanguageDetector.js:100` or otherwise produced a raw detected value, CRLF sequences in the attacker-controlled `lng` parameter reached `res.setHeader('Content-Language', ...)` verbatim.

### Impact

Two concrete outcomes depending on the Node.js version:

- **Node.js < 14.6.0 — HTTP response splitting.** An attacker crafting a request like `GET /?lng=en%0d%0aX-Injected%3A+malicious` could inject arbitrary additional HTTP response headers, enabling:
  - Session fixation via an injected `Set-Cookie`
  - Cache poisoning (injecting `Location`, `Content-Type`, etc.)
  - Reflected XSS in controlled response bodies
- **Node.js ≥ 14.6.0 — denial of service.** `res.setHeader()` throws `ERR_INVALID_CHAR` when the value contains CRLF. Because the middleware did not catch this error, it propagated as an unhandled exception, returning a 500 response to **all concurrent users sharing that process** (in worker-pool deployments this can knock out a full server instance).

The same header-setting code path fires inside the `languageChanged` event listener and again in the main middleware flow, so the flaw was triggered at least twice per affected request.

### Related (same release)

Version 3.9.3 also tightens the `hasXSS()` regex that was designed as a secondary filter on detected language values. The previous pattern `/<\s*\w+\s*on\w+\s*=.*?>/i` only matched event handlers in the **first** attribute position, so payloads like `<input autofocus onfocus=alert(1)>` bypassed the filter. Applications that rendered `res.locals.language` into HTML with a context-unsafe templating mode (EJS `<%- %>`, Pug `!{…}`, Handlebars `{{{…}}}`) could be XSSed despite the filter being in place. This bypass is noted here because it is fixed in the same release, but the primary vulnerability reported in this advisory is the CRLF/header-injection path above.

### Affected versions

`< 3.9.3`.

### Patch

Fixed in **3.9.3**. The patch introduces `utils.sanitizeHeaderValue(str)` which strips `\r`, `\n`, and other C0/C1 control characters, and replaces both `utils.escape(lng)` call sites in `lib/index.js` with it. The `hasXSS()` regex has also been tightened to match event-handler attributes at any position.

### Workarounds

No workaround short of upgrading. Front-proxying the middleware with a WAF rule that rejects `\r`/`\n` in query parameters, cookies, and path segments is a partial mitigation.

### Credits

Discovered via an internal security audit of the i18next ecosystem.

## References
- https://github.com/i18next/i18next-http-middleware/security/advisories/GHSA-c3h8-g69v-pjrg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41683
- https://github.com/i18next/i18next-http-middleware/commit/65301c194593d46a84623b64e5fde2f51d3550f6
- https://github.com/i18next/i18next-http-middleware
