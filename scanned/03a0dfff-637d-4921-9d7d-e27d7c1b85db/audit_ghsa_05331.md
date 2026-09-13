# [C] i18next-http-middleware: MissingKeyHandler does not reject keys whose segments contain prototype-polluting names

## Summary
Severity: Critical
Advisory: GHSA-f49m-vf83-692w
CVE: CVE-2026-48714
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-f49m-vf83-692w
Type: github-advisory

## Affected
- npm: `i18next-http-middleware` — affected >=0 <3.9.7

## Details
### Impact

`i18next-http-middleware` ≤ 3.9.6's `missingKeyHandler` blocked the literal request-body keys `__proto__`, `constructor`, and `prototype` (added in 3.9.3, see GHSA-5fgg-jcpf-8jjw), but did not reject dotted variants such as `"__proto__.polluted"`. Downstream backends that split the missing-key string on a configured `keySeparator` (notably `i18next-fs-backend` ≤ 2.6.5) hand these keys to an unguarded `setPath()` walker that writes to `Object.prototype`.

Applications that expose `missingKeyHandler` to untrusted input **AND** use `i18next-fs-backend` ≤ 2.6.5 are directly exploitable for remote prototype pollution. Other downstream backends that split the missing-key string the same way may be similarly affected.

Depending on the host application, polluted prototype properties may cause crashes, corrupted translation behaviour, configuration poisoning, or bypasses of property-based security checks.

### Patches

Fixed in **i18next-http-middleware 3.9.7**. A new `utils.hasUnsafeKeySegment(key, keySeparator)` helper is now used by `missingKeyHandler`; the configured `i18next.options.keySeparator` is honoured (default `.`; `false` disables segment splitting and only the literal-key denylist applies). Legitimate dotted keys (e.g. `"header.title"`) are unaffected.

The root-cause fix has been shipped in `i18next-fs-backend` **2.6.6** — see the companion advisory.

### Workarounds

If users cannot upgrade immediately:

- Do not expose `missingKeyHandler` to untrusted users (mount it behind authentication, or remove the route).
- Add a request-body filter ahead of the handler that rejects any top-level key containing `__proto__`, `constructor`, or `prototype` after splitting on a configured `keySeparator`.
- Disable missing-key persistence (`saveMissing: false`) when accepting writes from untrusted input.

### Resources

- Original report by [@codeswhite](https://github.com/codeswhite).
- Companion advisory in `i18next-fs-backend`: [GHSA-2933-q333-qg83](https://github.com/i18next/i18next-fs-backend/security/advisories/GHSA-2933-q333-qg83).
- Previous `i18next-http-middleware` security release: GHSA-5fgg-jcpf-8jjw and GHSA-c3h8-g69v-pjrg (in 3.9.3).

## References
- https://github.com/i18next/i18next-http-middleware/security/advisories/GHSA-f49m-vf83-692w
- https://nvd.nist.gov/vuln/detail/CVE-2026-48714
- https://github.com/i18next/i18next-http-middleware/commit/7c6d26f137d3e940b8d229ca148bca38845faf49
- https://github.com/i18next/i18next-http-middleware
