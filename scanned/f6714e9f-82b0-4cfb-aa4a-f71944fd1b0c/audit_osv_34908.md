# [H] ChurchCRM's Kiosk Manager Functions are vulnerable to Broken Access Control

## Summary
Severity: High
Advisory: CVE-2025-66397
Aliases: GHSA-32vr-ch3p-wmr5
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-66397
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 6.5.3, the allowRegistration, acceptKiosk, reloadKiosk, and identifyKiosk functions in the Kiosk Manager feature suffers from broken access control, allowing any authenticated user to allow and accept kiosk registrations, and perform other Kiosk Manager actions such as reload and identify. Version 6.5.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66397.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-32vr-ch3p-wmr5
- https://nvd.nist.gov/vuln/detail/CVE-2025-66397
