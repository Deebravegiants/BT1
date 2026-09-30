# [M] Handlebars.js has a Prototype Method Access Control Gap via Missing __lookupSetter__ Blocklist Entry

## Summary
Severity: Medium
Advisory: GHSA-7rx3-28cr-v5wh
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-7rx3-28cr-v5wh
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.6.0 <4.7.9

## Details
## Summary

The prototype method blocklist in `lib/handlebars/internal/proto-access.js` blocks `constructor`, `__defineGetter__`, `__defineSetter__`, and `__lookupGetter__`, but omits the symmetric `__lookupSetter__`. This omission is only exploitable when the non-default runtime option `allowProtoMethodsByDefault: true` is explicitly set — in that configuration `__lookupSetter__` becomes accessible while its counterparts remain blocked, creating an inconsistent security boundary.

`4.6.0` is the version that introduced `protoAccessControl` and the `allowProtoMethodsByDefault` runtime option.

## Description

In `lib/handlebars/internal/proto-access.js`:

```javascript
const methodWhiteList = Object.create(null);
methodWhiteList['constructor']      = false;
methodWhiteList['__defineGetter__'] = false;
methodWhiteList['__defineSetter__'] = false;
methodWhiteList['__lookupGetter__'] = false;
// __lookupSetter__ intentionally blocked in CVE-2021-23383,
// but omitted here — creating an asymmetric blocklist
```

All four legacy accessor helpers (`__defineGetter__`, `__defineSetter__`, `__lookupGetter__`, `__lookupSetter__`) were involved in the exploit chain addressed by CVE-2021-23383. Three of the four were explicitly blocked; `__lookupSetter__` was left out.

When `allowProtoMethodsByDefault: true` is set, any prototype method **not present** in `methodWhiteList` is permitted by default. Because `__lookupSetter__` is absent from the list, it passes the `checkWhiteList` check and is accessible in templates, while `__lookupGetter__` (its sibling) is correctly denied.

## Workarounds

- Do **not** set `allowProtoMethodsByDefault: true`. The default configuration is not affected.
- If `allowProtoMethodsByDefault` must be enabled, ensure templates do not reference  `__lookupSetter__` through untrusted input.

## References
- https://github.com/handlebars-lang/handlebars.js/security/advisories/GHSA-7rx3-28cr-v5wh
- https://github.com/advisories/GHSA-765h-qjxv-5f44
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.9
