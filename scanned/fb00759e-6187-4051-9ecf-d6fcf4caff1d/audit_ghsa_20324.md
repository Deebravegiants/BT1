# [H] Regular expression denial of service in devcert

## Summary
Severity: High
Advisory: GHSA-fp36-299x-pwmw
CVE: CVE-2022-1929
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-fp36-299x-pwmw
Type: github-advisory

## Affected
- npm: `devcert` — affected >=0 <1.2.1

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the devcert npm package, when an attacker is able to supply arbitrary input to the certificateFor method

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1929
- https://github.com/davewasmer/devcert/commit/b0763215f6683271d296fda98f7ef7bcd4a55977
- https://github.com/davewasmer/devcert
- https://research.jfrog.com/vulnerabilities/devcert-redos-xray-211352
