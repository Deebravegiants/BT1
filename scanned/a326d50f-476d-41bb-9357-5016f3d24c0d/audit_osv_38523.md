# [C] ChurchCRM: Authenticated Remote Code Execution via Unrestricted PHP File Write in Database Restore Function

## Summary
Severity: Critical
Advisory: CVE-2026-40484
Aliases: GHSA-2932-77f9-62fx
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40484
Type: osv

## Details
ChurchCRM is an open-source church management system. In versions prior to 7.2.0, the database backup restore functionality extracts uploaded archive contents and copies files from the Images/ directory into the web-accessible document root using recursiveCopyDirectory(), which performs no file extension filtering. An authenticated administrator can upload a crafted backup archive containing a PHP webshell inside the Images/ directory, which is then written to a publicly accessible path and executable via HTTP requests, resulting in remote code execution as the web server user. The restore endpoint also lacks CSRF token validation, enabling exploitation through cross-site request forgery targeting an authenticated administrator. This issue has been fixed in version 7.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40484.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-2932-77f9-62fx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40484
- https://github.com/ChurchCRM/CRM/commit/68be1d12bc4cc1429575ae797ef05efe47030d39
- https://github.com/ChurchCRM/CRM/pull/8610
