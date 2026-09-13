# [C] code-server vulnerable to Missing Origin Validation in WebSockets

## Summary
Severity: Critical
Advisory: GHSA-frjg-g767-7363
CVE: CVE-2023-26114
CWE: CWE-1385, CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-frjg-g767-7363
Type: github-advisory

## Affected
- npm: `code-server` — affected >=0 <4.10.1

## Details
Versions of the package code-server before 4.10.1 are vulnerable to Missing Origin Validation in WebSockets handshakes. Exploiting this vulnerability can allow an adversary in specific scenarios to access data from and connect to the code-server instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26114
- https://github.com/coder/code-server/commit/d477972c68fc8c8e8d610aa7287db87ba90e55c7
- https://github.com/coder/code-server
- https://github.com/coder/code-server/releases/tag/v4.10.1
- https://security.snyk.io/vuln/SNYK-JS-CODESERVER-3368148
