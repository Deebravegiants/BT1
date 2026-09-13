# [C] ChurchCRM discloses database information on error message

## Summary
Severity: Critical
Advisory: CVE-2025-68110
Aliases: GHSA-82mq-xc2j-3qv2
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68110
Type: osv

## Details
ChurchCRM is an open-source church management system. Versions prior to 6.5.3 may disclose database information in an error message including the host, ip, username, and password. Version 6.5.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68110.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-82mq-xc2j-3qv2
- https://nvd.nist.gov/vuln/detail/CVE-2025-68110
