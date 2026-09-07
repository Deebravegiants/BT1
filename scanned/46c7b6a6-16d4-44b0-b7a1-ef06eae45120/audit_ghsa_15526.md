# [M] MindsDB Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-32fj-r8qw-r8w8
CVE: CVE-2024-45856
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-12
Source: https://github.com/advisories/GHSA-32fj-r8qw-r8w8
Type: github-advisory

## Affected
- PyPI: `mindsdb` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability exists in all versions of the MindsDB platform, enabling the execution of a JavaScript payload whenever a user enumerates an ML Engine, database, project, or dataset containing arbitrary JavaScript code within the web UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45856
- https://hiddenlayer.com/sai-security-advisory/2024-09-mindsdb
