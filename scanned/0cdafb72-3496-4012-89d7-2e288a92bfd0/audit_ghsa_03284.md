# [C] Command Injection in ps-visitor

## Summary
Severity: Critical
Advisory: GHSA-v2jv-33gh-xx29
CVE: CVE-2021-23374
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-v2jv-33gh-xx29
Type: github-advisory

## Affected
- npm: `ps-visitor` — affected >=0

## Details
This affects all versions up to and including version 0.0.2 of package ps-visitor. If attacker-controlled user input is given to the kill function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23374
- https://github.com/WisdomKwan/ps-visitor
- https://github.com/WisdomKwan/ps-visitor/blob/cdfc934a8e4af95aa0473f4b2a4bd091d09faf2f/index.js#23L404
- https://snyk.io/vuln/SNYK-JS-PSVISITOR-1078544
