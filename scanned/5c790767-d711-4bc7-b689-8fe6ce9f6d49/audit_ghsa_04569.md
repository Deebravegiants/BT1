# [C] i18next-fs-backend vulnerable to prototype pollution via crafted missing-key string

## Summary
Severity: Critical
Advisory: GHSA-2933-q333-qg83
CVE: CVE-2026-48713
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-2933-q333-qg83
Type: github-advisory

## Affected
- npm: `i18next-fs-backend` — affected >=0 <2.6.6

## Details
### Impact

`i18next-fs-backend` ≤ 2.6.5, when used to persist missing translation keys (e.g. via `i18next-http-middleware`'s `missingKeyHandler` exposed to untrusted input), is vulnerable to prototype pollution via crafted missing-key strings.

`Backend.writeFile()` splits each queued missing-key string on the configured `keySeparator` (default `.`) before calling the internal `setPath()` walker. The walker (`getLastOfPath` in `lib/utils.js`) did not guard against unsafe segments, so a key like `"__proto__.polluted"` was split into `["__proto__", "polluted"]` and walked straight into `Object.prototype`, allowing an attacker to write arbitrary properties onto the global object prototype.

Depending on the host application, polluted prototype properties may cause crashes, corrupted translation behaviour, configuration poisoning, or bypasses of property-based security checks.

### Affected configuration

Applications are directly affected only if **all** of the following hold:

- `i18next-fs-backend` ≤ 2.6.5 is configured as the backend.
- `i18next-http-middleware`'s `missingKeyHandler` (or another route that forwards untrusted request bodies to `i18next.t(..., { ... })` with `saveMissing: true`) is reachable by untrusted users.
- The default behaviour of splitting missing-key strings on `keySeparator` is in use (i.e. `keySeparator` is not `false`).

Apps that do not expose missing-key persistence to untrusted input are not directly affected through this attack path.

### Patches

Fixed in **i18next-fs-backend 2.6.6**. The traversal helper now refuses to descend through `__proto__`, `constructor`, or `prototype` segments and drops the offending write silently. Legitimate dotted keys (e.g. `"header.title"`) are unaffected.

A matching defence-in-depth fix has been shipped in `i18next-http-middleware` **3.9.7** — see the companion advisory.

### Workarounds

If users cannot upgrade immediately:

- Do not expose `i18next-http-middleware`'s `missingKeyHandler` to untrusted users (mount it behind authentication, or remove the route).
- Disable missing-key persistence (`saveMissing: false`, or no `backend.create` implementation) when accepting writes from untrusted input.
- Set `keySeparator: false` in the i18next options to disable backend key splitting (note: this also disables nested translation keys).

### Resources

- Original report by [@codeswhite](https://github.com/codeswhite).
- Companion advisory in `i18next-http-middleware`: [GHSA-f49m-vf83-692w](https://github.com/i18next/i18next-http-middleware/security/advisories/GHSA-f49m-vf83-692w).
- Previous `i18next-fs-backend` security release: GHSA-8847-338w-5hcj (path traversal via `lng`/`ns`, fixed in 2.6.4).

## References
- https://github.com/i18next/i18next-fs-backend/security/advisories/GHSA-2933-q333-qg83
- https://nvd.nist.gov/vuln/detail/CVE-2026-48713
- https://github.com/i18next/i18next-fs-backend/commit/3ab0448087da6935a40117f904b7457281f963f4
- https://github.com/i18next/i18next-fs-backend
