# [H] Prototype Pollution in sds

## Summary
Severity: High
Advisory: GHSA-ph28-wwfj-fv7f
CVE: CVE-2022-25862
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-ph28-wwfj-fv7f
Type: github-advisory

## Affected
- npm: `sds` — affected >=0

## Details
This affects the package sds from 0.0.0. The library could be tricked into adding or modifying properties of the Object.prototype by abusing the set function located in js/set.js. **Note:** This vulnerability derives from an incomplete fix to CVE-2020-7618

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7618
- https://nvd.nist.gov/vuln/detail/CVE-2022-25862
- https://github.com/monsterkodi/sds
- https://github.com/monsterkodi/sds/blob/master/js/set.js
- https://snyk.io/vuln/SNYK-JS-SDS-2385944
