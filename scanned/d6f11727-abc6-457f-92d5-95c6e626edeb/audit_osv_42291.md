# [C] phpMyFAQ before 4.1.6 Path Traversal via category image deletion

## Summary
Severity: Critical
Advisory: CVE-2026-66397
Aliases: GHSA-mh9w-5hr8-3272
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66397
Type: osv

## Details
phpMyFAQ before 4.1.6 fails to validate path traversal sequences in the existing_image field during category updates, allowing authenticated attackers to delete arbitrary files by exploiting insufficient sanitization in Image::delete(). Attackers can delete the database.php configuration file to disable the installation gate and access the public setup wizard to create new superadmin accounts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66397.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-mh9w-5hr8-3272
- https://nvd.nist.gov/vuln/detail/CVE-2026-66397
- https://www.vulncheck.com/advisories/phpmyfaq-before-path-traversal-via-category-image-deletion
