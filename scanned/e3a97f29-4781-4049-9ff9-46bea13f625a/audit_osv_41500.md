# [H] Wallos: Zip Slip path traversal in database restore writes files to webroot

## Summary
Severity: High
Advisory: CVE-2026-61639
Aliases: GHSA-3vg2-cxpg-m43g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-61639
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.6, POST /endpoints/db/restore.php calls ZipArchive::extractTo() without validating entry names for ../ sequences. Admin uploads crafted zip with entry logos/../../endpoints/shell.php to write webshell to webroot. Extension filter only applies to post-extraction logo copy step. This issue has been patched in version 4.9.6.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61639.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-3vg2-cxpg-m43g
- https://nvd.nist.gov/vuln/detail/CVE-2026-61639
- https://github.com/ellite/Wallos/commit/b75f13d0ffa3ed7e77e8e79e4b9fd3fc528c98d3
- https://github.com/ellite/Wallos/pull/1092
