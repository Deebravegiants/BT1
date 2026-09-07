# [C] Authentication Bypass in console-io

## Summary
Severity: Critical
Advisory: GHSA-q52j-4q2q-hcj6
CVE: CVE-2016-10532
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-q52j-4q2q-hcj6
Type: github-advisory

## Affected
- npm: `console-io` — affected >=0 <2.3.0

## Details
Affected versions of the `console-io` package do not configure the underlying websocket library to require authentication, resulting in an authentication bypass vulnerability. As `console-io` allows terminal access on the server via a web page, an authentication bypass is essentially remote code execution.



## Recommendation

Update to version 2.3.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10532
- https://github.com/advisories/GHSA-q52j-4q2q-hcj6
- https://www.npmjs.com/advisories/90
