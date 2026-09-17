# [M] @blakeembrey/template vulnerable to code injection when attacker controls template input

## Summary
Severity: Medium
Advisory: GHSA-q765-wm9j-66qj
CVE: CVE-2024-45390
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-q765-wm9j-66qj
Type: github-advisory

## Affected
- npm: `@blakeembrey/template` — affected >=0 <1.2.0

## Details
### Impact

It is possible to inject and run code within the template if the attacker has access to write the template name.

```js
const { template } = require('@blakeembrey/template');

template("Hello {{name}}!", "exploit() {} && ((()=>{ console.log('success'); })()) && function pwned");
```

### Patches

Upgrade to 1.2.0.

### Workarounds

Don't pass untrusted input as the template display name, or don't use the display name feature.

### References

Fixed by removing in https://github.com/blakeembrey/js-template/commit/b8d9aa999e464816c6cfb14acd1ad0f5d1e335aa.

## References
- https://github.com/blakeembrey/js-template/security/advisories/GHSA-q765-wm9j-66qj
- https://nvd.nist.gov/vuln/detail/CVE-2024-45390
- https://github.com/blakeembrey/js-template/commit/b8d9aa999e464816c6cfb14acd1ad0f5d1e335aa
- https://github.com/blakeembrey/js-template
