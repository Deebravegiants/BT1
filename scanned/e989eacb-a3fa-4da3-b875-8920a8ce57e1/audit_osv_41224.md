# [M] ChurchCRM : Broken Access Control in `CSVCreateFile.php` Allows Low-Privileged Users to Export All Members' PII

## Summary
Severity: Medium
Advisory: CVE-2026-58408
Aliases: GHSA-4vj2-gm78-3q63
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-58408
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 7.4.0, a low-privileged user can bypass the /admin/export UI and exfiltrate the entire member directory. The POST /CSVCreateFile.php endpoint generates and streams a CSV containing the full Personally Identifiable Information (PII) of every Person/Family record in the database, without performing any feature-level or object-level authorization check beyond the coarse "has any admin permission" gate inherited from the legacy page bootstrap. In other words, any single non-admin permission flag is enough to reach the CSV bulk-export endpoint, even though such users should not have data export rights. The export script is missing a dedicated isAdmin() (or a new bExportData) authorization check of its own. This issue has been fixed in version 7.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58408.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-4vj2-gm78-3q63
- https://nvd.nist.gov/vuln/detail/CVE-2026-58408
