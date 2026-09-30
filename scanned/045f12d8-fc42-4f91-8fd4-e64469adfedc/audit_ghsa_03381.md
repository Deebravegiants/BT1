# [H] OS Command Injection in im-resize

## Summary
Severity: High
Advisory: GHSA-r9vm-rhmf-7hxx
CVE: CVE-2019-10787
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-r9vm-rhmf-7hxx
Type: github-advisory

## Affected
- npm: `im-resize` — affected >=0

## Details
im-resize through 2.3.2 allows remote attackers to execute arbitrary commands via the "exec" argument. The cmd argument used within index.js, can be controlled by user without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10787
- https://github.com/Turistforeningen/node-im-resize/commit/de624dacf6a50e39fe3472af1414d44937ce1f03
- https://snyk.io/vuln/SNYK-JS-IMRESIZE-544183
