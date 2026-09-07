# [M] gettext-converter: Prototype pollution in js2i18next() via crafted translation keys

## Summary
Severity: Medium
Advisory: GHSA-f4jp-rw7w-ccwg
CVE: CVE-2026-55451
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-f4jp-rw7w-ccwg
Type: github-advisory

## Affected
- npm: `gettext-converter` — affected >=0 <1.3.3

## Details
### Impact

`js2i18next()` is vulnerable to prototype pollution. When converting translations, it splits nested keys on the key separator (default `##`) and uses each segment as a dynamic object key while building the output object. A key whose segment is `__proto__` (e.g. `__proto__##gcPolluted`) causes the converter to resolve `Object.prototype` as the nested write target and assign the translated value onto it, polluting `Object.prototype` for the whole runtime.

Any application that converts translation data (PO / i18next JS objects) originating from an untrusted or user-controlled source is affected. Prototype pollution can lead to denial of service and, depending on the surrounding application, may enable further attacks.

### Patches

Fixed in `gettext-converter@1.3.3`. Key segments equal to `__proto__`, `constructor`, or `prototype` are now rejected before being used as dynamic object keys.

### Workarounds

Upgrade to `1.3.3`. If upgrading is not immediately possible, sanitize/validate translation keys before passing them to `js2i18next()` and reject any key whose `##`-separated segments include `__proto__`, `constructor`, or `prototype`.

## References
- https://github.com/locize/gettext-converter/security/advisories/GHSA-f4jp-rw7w-ccwg
- https://github.com/locize/gettext-converter/issues/15
- https://github.com/locize/gettext-converter/commit/df90c3b93e51faef68891d97b626544f619c5b31
- https://github.com/locize/gettext-converter
- https://github.com/locize/gettext-converter/releases/tag/v1.3.3
