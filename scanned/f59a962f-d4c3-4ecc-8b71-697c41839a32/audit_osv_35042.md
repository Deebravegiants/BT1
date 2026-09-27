# [C] ChurchCRM vulnerable to RCE with database restore functionality

## Summary
Severity: Critical
Advisory: CVE-2025-68109
Aliases: GHSA-pqm7-g8px-9r77
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68109
Type: osv

## Details
ChurchCRM is an open-source church management system. In versions prior to 6.5.3, the Database Restore functionality does not validate the content or file extension of uploaded files. As a result, an attacker can upload a web shell file and subsequently upload a .htaccess file to enable direct access to it. Once accessed, the uploaded web shell allows remote code execution (RCE) on the server. Version 6.5.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68109.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-pqm7-g8px-9r77
- https://nvd.nist.gov/vuln/detail/CVE-2025-68109
