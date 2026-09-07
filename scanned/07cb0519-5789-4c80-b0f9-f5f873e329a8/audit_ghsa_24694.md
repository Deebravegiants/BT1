# [M] Cross site scripting in code-server

## Summary
Severity: Medium
Advisory: GHSA-2gp3-6c9p-jp7w
CVE: CVE-2021-42648
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-12
Source: https://github.com/advisories/GHSA-2gp3-6c9p-jp7w
Type: github-advisory

## Affected
- npm: `code-server` — affected >=0 <3.12.0

## Details
Cross-site scripting (XSS) vulnerability exists in Coder Code-Server before 3.12.0, allows attackers to execute arbitrary code via crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42648
- https://github.com/cdr/code-server/issues/4355
- https://github.com/coder/code-server/pull/4430
- https://github.com/coder/code-server
