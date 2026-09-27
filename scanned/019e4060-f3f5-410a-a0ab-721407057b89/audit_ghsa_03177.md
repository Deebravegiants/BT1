# [C] Prototype Pollution in connie-lang

## Summary
Severity: Critical
Advisory: GHSA-8vv3-jxm8-f4vf
CVE: CVE-2020-7706
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-8vv3-jxm8-f4vf
Type: github-advisory

## Affected
- npm: `connie-lang` — affected >=0 <0.1.1

## Details
The package connie-lang before 0.1.1 are vulnerable to Prototype Pollution in the configuration language library used by connie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7706
- https://github.com/mattinsler/connie-lang/commit/ef376d404c712dd28309ba07f28a8f87f24a015a
- https://snyk.io/vuln/SNYK-JS-CONNIELANG-598853
