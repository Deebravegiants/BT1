# [C] Command Injection in macfromip

## Summary
Severity: Critical
Advisory: GHSA-vh8f-xw5v-8993
CVE: CVE-2020-7786
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-12
Source: https://github.com/advisories/GHSA-vh8f-xw5v-8993
Type: github-advisory

## Affected
- npm: `macfromip` — affected >=0

## Details
All versions of npm package macfromip are affected by a command injection vulnerability. The injection point is located in line 66 in macfromip.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7786
- https://snyk.io/vuln/SNYK-JS-MACFROMIP-1048336
- https://www.npmjs.com/package/macfromip
