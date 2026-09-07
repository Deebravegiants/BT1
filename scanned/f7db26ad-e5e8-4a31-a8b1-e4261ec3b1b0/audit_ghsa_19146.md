# [H] Leantime allows Cross Site Scripting (XSS) and SQL Injection (SQLi)

## Summary
Severity: High
Advisory: GHSA-v4q9-437p-mhpg
CWE: CWE-79, CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-v4q9-437p-mhpg
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0 <3.3

## Details
### Summary
A cross-site scripting (XSS) vulnerability has been identified in Leantime. The vulnerability allows an attacker to inject malicious scripts into certain fields, potentially leading to the execution of arbitrary code or unauthorized access to user-sensitive information. The code does not include any validation or sanitization of the $_GET["id"] parameter. As a result, it directly incorporates the user-supplied value into the source path without any checks.

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-v4q9-437p-mhpg
- https://github.com/Leantime/leantime
