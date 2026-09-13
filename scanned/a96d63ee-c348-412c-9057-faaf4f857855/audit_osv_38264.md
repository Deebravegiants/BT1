# [C] ChurchCRM has a Path traversal leads to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-35573
Aliases: GHSA-r6cr-mvr9-f6wx
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35573
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to 6.5.3, a path traversal vulnerability in ChurchCRM's backup restore functionality allows authenticated administrators to upload arbitrary files and achieve remote code execution by overwriting Apache .htaccess configuration files. The vulnerability exists in src/ChurchCRM/Backup/RestoreJob.php. The $rawUploadedFile['name'] parameter is user-controlled and allows uploading files with arbitrary names to /var/www/html/tmp_attach/ChurchCRMBackups/. This vulnerability is fixed in 6.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35573.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-r6cr-mvr9-f6wx
- https://nvd.nist.gov/vuln/detail/CVE-2026-35573
