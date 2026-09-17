# [M] jodit: Prototype pollution in Jodit via Jodit.modules.Helpers.set()

## Summary
Severity: Medium
Advisory: GHSA-vpmm-x3fm-qr5c
CVE: CVE-2026-55886
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-vpmm-x3fm-qr5c
Type: github-advisory

## Affected
- npm: `jodit` — affected >=0 <4.12.26

## Details
### Summary
`Jodit.modules.Helpers.set(chain, value, obj)` walks the dot-separated `chain`, creating and following each path segment, without filtering prototype-mutating keys. A chain that begins with (or contains) `__proto__`, `constructor`, or `prototype` lets the final assignment reach and mutate `Object.prototype` (prototype pollution).

### Affected
- Package: `jodit` (npm)
- Versions: `< 4.12.26`
- Public API: `Jodit.modules.Helpers.set(chain, value, obj)`

### Proof of Concept
```js
const { Jodit } = require('jodit');
delete Object.prototype.polluted;
Jodit.modules.Helpers.set('__proto__.polluted', 'yes', {});
console.log(({}).polluted); // "yes" (before the fix)
delete Object.prototype.polluted;
```

### Impact
Applications that pass a user-controlled or partially user-controlled key path into `Jodit.modules.Helpers.set()` could be vulnerable to prototype pollution (CWE-1321): unexpected property injection, logic bypass, denial of service, or secondary security issues.

### Patch
Fixed in 4.12.26 by rejecting any `chain` whose segments include `__proto__`, `constructor`, or `prototype`, reusing the same guard introduced for `Jodit.configure()` in 4.12.18.

### Credit
Responsibly reported by Junming Wu.

## References
- https://github.com/xdan/jodit/security/advisories/GHSA-vpmm-x3fm-qr5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-55886
- https://github.com/xdan/jodit
