# [H] phpMyFAQ before 4.1.6 Privilege Escalation via Group Membership

## Summary
Severity: High
Advisory: CVE-2026-66399
Aliases: GHSA-28cc-v39j-vr95
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66399
Type: osv

## Details
phpMyFAQ before 4.1.6 contains a privilege escalation vulnerability in GroupController::updateMembers() that allows administrators with only group-management permissions to join privileged groups without verification of required rights. Attackers can add themselves to pre-existing groups holding user-management rights and immediately inherit those permissions to modify or delete user accounts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66399.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-28cc-v39j-vr95
- https://nvd.nist.gov/vuln/detail/CVE-2026-66399
- https://www.vulncheck.com/advisories/phpmyfaq-before-privilege-escalation-via-group-membership
