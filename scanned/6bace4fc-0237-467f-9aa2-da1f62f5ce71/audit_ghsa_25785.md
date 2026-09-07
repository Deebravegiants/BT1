# [C] Prototype Pollution in libnested

## Summary
Severity: Critical
Advisory: GHSA-x5m8-2r8v-8f97
CVE: CVE-2022-25352
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-x5m8-2r8v-8f97
Type: github-advisory

## Affected
- npm: `libnested` — affected >=0 <1.5.2

## Details
The package libnested before 1.5.2 are vulnerable to Prototype Pollution via the set function in index.js. **Note:** This vulnerability derives from an incomplete fix for [CVE-2020-28283](https://security.snyk.io/vuln/SNYK-JS-LIBNESTED-1054930)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25352
- https://github.com/dominictarr/libnested/commit/c1129865d75fbe52b5a4f755ad3110ca5420f2e1
- https://github.com/dominictarr/libnested
- https://github.com/dominictarr/libnested/blob/master/index.js%23L22
- https://snyk.io/vuln/SNYK-JS-LIBNESTED-2342117
