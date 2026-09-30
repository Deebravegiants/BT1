# [M] Uncontrolled Resource Consumption in markdown-it

## Summary
Severity: Medium
Advisory: GHSA-6vfc-qv3f-vr6c
CVE: CVE-2022-21670
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-6vfc-qv3f-vr6c
Type: github-advisory

## Affected
- npm: `markdown-it` — affected >=0 <12.3.2

## Details
### Impact

Special patterns with length > 50K chars can slow down parser significantly.

```js
const md = require('markdown-it')();

md.render(`x ${' '.repeat(150000)} x  \nx`);
```


### Patches

Upgrade to v12.3.2+

### Workarounds

No.

### References

Fix + test sample: https://github.com/markdown-it/markdown-it/commit/ffc49ab46b5b751cd2be0aabb146f2ef84986101

## References
- https://github.com/markdown-it/markdown-it/security/advisories/GHSA-6vfc-qv3f-vr6c
- https://nvd.nist.gov/vuln/detail/CVE-2022-21670
- https://github.com/markdown-it/markdown-it/commit/ffc49ab46b5b751cd2be0aabb146f2ef84986101
- https://github.com/markdown-it/markdown-it
