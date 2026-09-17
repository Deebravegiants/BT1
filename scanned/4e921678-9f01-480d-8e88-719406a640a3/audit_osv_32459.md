# [H] WeGIA Vulnerable to Broken Authentication - Old Password Validation

## Summary
Severity: High
Advisory: CVE-2025-30361
Aliases: GHSA-m6qw-r3m9-jf7h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:L/SI:H/SA:L)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-30361
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. A security vulnerability was identified in versions prior to 3.2.6, where it is possible to change a user's password without verifying the old password. This issue exists in the control.php endpoint and allows unauthorized attackers to bypass authentication and authorization mechanisms to reset the password of any user, including admin accounts. Version 3.2.6 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30361.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-m6qw-r3m9-jf7h
- https://nvd.nist.gov/vuln/detail/CVE-2025-30361
