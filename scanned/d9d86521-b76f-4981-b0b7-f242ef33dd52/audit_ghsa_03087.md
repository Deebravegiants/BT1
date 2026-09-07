# [C] Command Injection in picotts

## Summary
Severity: Critical
Advisory: GHSA-wq7q-5v6j-xfv6
CVE: CVE-2021-23378
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-wq7q-5v6j-xfv6
Type: github-advisory

## Affected
- npm: `picotts` — affected >=0

## Details
This affects all versions up to and including version 0.1.1 of package picotts. If attacker-controlled user input is given to the say function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23378
- https://github.com/luisivan/node-picotts
- https://github.com/luisivan/node-picotts/blob/8c6b183b884890c8e9422f93036b374942398c8b/index.js#23L16
- https://snyk.io/vuln/SNYK-JS-PICOTTS-1078539
