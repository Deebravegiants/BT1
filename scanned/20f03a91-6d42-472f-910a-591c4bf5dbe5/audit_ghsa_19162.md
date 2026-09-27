# [M] Leantime has Host Header Injection Vulnerability 

## Summary
Severity: Medium
Advisory: GHSA-99r5-84gr-59f6
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-99r5-84gr-59f6
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0 <3.1.2

## Details
### Summary
A host header injection vulnerability has been identified in the user details viewing functionality of the system. This vulnerability allows an attacker to manipulate the host header in HTTP requests, thereby gaining unauthorized access to view details of other users.

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-99r5-84gr-59f6
- https://github.com/Leantime/leantime
