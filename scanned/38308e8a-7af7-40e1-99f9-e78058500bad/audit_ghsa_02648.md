# [H] OS Command Injection in ssh2

## Summary
Severity: High
Advisory: GHSA-652h-xwhf-q4h6
CVE: CVE-2020-26301
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-09-21
Source: https://github.com/advisories/GHSA-652h-xwhf-q4h6
Type: github-advisory

## Affected
- npm: `ssh2` — affected >=0 <1.4.0

## Details
ssh2 is client and server modules written in pure JavaScript for node.js. In ssh2 before version 1.4.0 there is a command injection vulnerability. The issue only exists on Windows. This issue may lead to remote code execution if a client of the library calls the vulnerable method with untrusted input. This is fixed in version 1.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26301
- https://github.com/mscdex/ssh2/commit/f763271f41320e71d5cbee02ea5bc6a2ded3ca21
- https://github.com/mscdex/ssh2
- https://securitylab.github.com/advisories/GHSL-2020-123-mscdex-ssh2
- https://www.npmjs.com/package/ssh2
