# [H] Jenkins Simple Queue Plugin has stored cross-site scripting (XSS) vulnerability

## Summary
Severity: High
Advisory: GHSA-4gwv-fpmg-cmv2
CVE: CVE-2024-54003
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-4gwv-fpmg-cmv2
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:simple-queue` — affected >=0 <1.4.5

## Details
Jenkins Simple Queue Plugin 1.4.4 and earlier does not escape the view name.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with View/Create permission.

Simple Queue Plugin 1.4.5 escapes the view name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-54003
- https://www.jenkins.io/security/advisory/2024-11-27/#SECURITY-3467
