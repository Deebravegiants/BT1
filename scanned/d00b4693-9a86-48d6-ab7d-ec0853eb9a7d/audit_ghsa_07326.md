# [M] Jodit has prototype pollution via Jodit.configure() / ConfigMerge

## Summary
Severity: Medium
Advisory: GHSA-5957-5c94-3v7w
CVE: CVE-2026-54756
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-5957-5c94-3v7w
Type: github-advisory

## Affected
- npm: `jodit` — affected >=0 <4.12.18

## Details
### Summary
`Jodit.configure(options)` — and the internal `ConfigMerge` / `ConfigProto` helpers — merged user-supplied options into the editor configuration without filtering prototype-mutating keys. A payload nested under an existing plain-object option such as `controls` could reach and mutate `Object.prototype` (prototype pollution).

### Affected
- Package: `jodit` (npm)
- Versions: `< 4.12.18`
- Public API: `Jodit.configure(options)`

### Proof of Concept
```js
import { Jodit } from 'jodit';
delete Object.prototype.polluted;
Jodit.configure(JSON.parse('{"controls":{"__proto__":{"polluted":"yes"}}}'));
console.log(({}).polluted); // "yes" (before the fix)
delete Object.prototype.polluted;
```

### Impact
Applications that pass user-controlled or partially user-controlled configuration into `Jodit.configure()` could be vulnerable to prototype pollution: unexpected property injection, logic bypass, denial of service, or secondary security issues.

### Patch
Fixed in 4.12.18 by rejecting `__proto__`, `constructor`, and `prototype` at every merge level in `ConfigMerge` and `ConfigProto`.

### Credit
Responsibly reported by Junming Wu.

## References
- https://github.com/xdan/jodit/security/advisories/GHSA-5957-5c94-3v7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54756
- https://github.com/xdan/jodit/commit/d298397bc993793b17145806c15f7dae53f90104
- https://github.com/xdan/jodit
- https://github.com/xdan/jodit/releases/tag/4.12.18
