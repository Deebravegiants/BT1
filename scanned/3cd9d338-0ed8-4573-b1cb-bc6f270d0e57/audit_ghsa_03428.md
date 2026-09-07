# [H] Command Injection in killport

## Summary
Severity: High
Advisory: GHSA-fc42-h7q4-qp8h
CVE: CVE-2021-23360
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-fc42-h7q4-qp8h
Type: github-advisory

## Affected
- npm: `killport` — affected >=0 <1.0.2

## Details
This affects the package killport before 1.0.2. If (attacker-controlled) user input is given, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization. Running this PoC will cause the command touch success to be executed, leading to the creation of a file called success.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23360
- https://github.com/ssnau/killport/commit/bec8e371f170a12e11cd222ffc7a6e1ae9942638
- https://github.com/ssnau/killport/blob/5268f23ea8f152e47182b263d8f7ef20c12a9f28/index.js%23L9
- https://snyk.io/vuln/SNYK-JS-KILLPORT-1078535
