# [M] validator.js has a URL validation bypass vulnerability in its isURL function

## Summary
Severity: Medium
Advisory: GHSA-9965-vmph-33xx
CVE: CVE-2025-56200
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-9965-vmph-33xx
Type: github-advisory

## Affected
- npm: `validator` — affected >=0 <13.15.20

## Details
A URL validation bypass vulnerability exists in validator.js prior to version 13.15.20. The isURL() function uses '://' as a delimiter to parse protocols, while browsers use ':' as the delimiter. This parsing difference allows attackers to bypass protocol and domain validation by crafting URLs leading to XSS and Open Redirect attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56200
- https://github.com/validatorjs/validator.js/issues/2600
- https://github.com/validatorjs/validator.js/pull/2608
- https://github.com/validatorjs/validator.js/commit/cbef5088f02d36caf978f378bb845fe49bdc0809
- https://gist.github.com/junan-98/27ae092aa40e2a057d41a0f95148f666
- https://gist.github.com/junan-98/a93130505b258b9e4ec9f393e7533596
- https://github.com/validatorjs/validator.js
- https://github.com/validatorjs/validator.js/releases/tag/13.15.20
- http://validatorjs.com
