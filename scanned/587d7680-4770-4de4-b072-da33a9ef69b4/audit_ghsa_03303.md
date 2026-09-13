# [H] Command Injection in killing

## Summary
Severity: High
Advisory: GHSA-cq77-8jpx-892g
CVE: CVE-2021-23381
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-cq77-8jpx-892g
Type: github-advisory

## Affected
- npm: `killing` — affected >=0

## Details
This affects all versions of package killing up to and including 1.0.6. If attacker-controlled user input is given, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23381
- https://github.com/xudafeng/killing
- https://github.com/xudafeng/killing/blob/672ed164ccdd10c0a8fb93c5c6d2456f1dfab781/lib/killing.js%23L62
- https://snyk.io/vuln/SNYK-JS-KILLING-1078532
- https://www.npmjs.com/package/killing
