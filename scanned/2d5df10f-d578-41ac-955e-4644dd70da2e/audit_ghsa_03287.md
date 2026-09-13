# [H] Arbitrary Code Execution in shiba

## Summary
Severity: High
Advisory: GHSA-jvf4-g24p-2qgw
CVE: CVE-2020-7738
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-jvf4-g24p-2qgw
Type: github-advisory

## Affected
- npm: `shiba` — affected >=0

## Details
All versions of package shiba are vulnerable to Arbitrary Code Execution due to the default usage of the function `load()` of the package js-yaml instead of its secure replacement , `safeLoad()`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7738
- https://snyk.io/vuln/SNYK-JS-SHIBA-596466
- https://www.npmjs.com/package/shiba
