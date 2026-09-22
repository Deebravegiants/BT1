# [C] OS Command injection in npm-lockfile

## Summary
Severity: Critical
Advisory: GHSA-cr6m-62pq-hmqh
CVE: CVE-2022-0841
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-04
Source: https://github.com/advisories/GHSA-cr6m-62pq-hmqh
Type: github-advisory

## Affected
- npm: `npm-lockfile` — affected >=2.0.3 <2.0.5

## Details
npm-lockfile safely generates an npm lockfile and output it to the filename of your choice. npm-lockfile before 2.0.4 does not santize unsafe external input and invoke sensitive command execution API with the input, causing command injection vulnerability. A fix was released in version 2.0.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0841
- https://github.com/ljharb/npm-lockfile/commit/bfdb84813260f0edbf759f2fde1e8c816c1478b8
- https://github.com/ljharb/npm-lockfile
- https://huntr.dev/bounties/4f806dc9-2ecd-4e79-997e-5292f1bea9f1
