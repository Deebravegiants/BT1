# [M] Lodash has Prototype Pollution Vulnerability in `_.unset` and `_.omit` functions

## Summary
Severity: Medium
Advisory: GHSA-xxjr-mmjv-4gpg
CVE: CVE-2025-13465
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-xxjr-mmjv-4gpg
Type: github-advisory

## Affected
- npm: `lodash` — affected >=4.0.0 <4.17.23
- npm: `lodash.unset` — affected >=4.0.0
- npm: `lodash-es` — affected >=4.0.0 <4.17.23
- npm: `lodash-amd` — affected >=4.0.0 <4.17.23

## Details
### Impact

Lodash versions 4.0.0 through 4.17.22 are vulnerable to prototype pollution in the `_.unset` and `_.omit` functions. An attacker can pass crafted paths which cause Lodash to delete methods from global prototypes. 

The issue permits deletion of properties but does not allow overwriting their original behavior.  

### Patches

This issue is patched on 4.17.23.

## References
- https://github.com/lodash/lodash/security/advisories/GHSA-xxjr-mmjv-4gpg
- https://nvd.nist.gov/vuln/detail/CVE-2025-13465
- https://github.com/lodash/lodash/commit/edadd452146f7e4bad4ea684e955708931d84d81
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://github.com/lodash/lodash
