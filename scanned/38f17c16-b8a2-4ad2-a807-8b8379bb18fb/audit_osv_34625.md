# [H] my little forum vulnerable to SQL Injection in Bookmark Reordering via bookmarks parameter

## Summary
Severity: High
Advisory: CVE-2025-62606
Aliases: GHSA-m8hj-c6gr-6h6v
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2025-62606
Type: osv

## Details
my little forum is a PHP and MySQL based internet forum that displays the messages in classical threaded view. Prior to version 2.5.12, an authenticated SQL injection vulnerability in the bookmark reordering feature allows any logged-in user to execute arbitrary SQL commands. This can lead to a full compromise of the application's database, including reading, modifying, or deleting all data. This issue has been patched in version 2.5.12.

## References
- https://github.com/My-Little-Forum/mylittleforum/releases/tag/20251021.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62606.json
- https://github.com/My-Little-Forum/mylittleforum/security/advisories/GHSA-m8hj-c6gr-6h6v
- https://nvd.nist.gov/vuln/detail/CVE-2025-62606
