# [H] Vvveb product revision authorization bypass allows Vendors to read, restore, or delete other Vendors' product revisions

## Summary
Severity: High
Advisory: CVE-2026-49225
Aliases: GHSA-gmrp-ccwf-xggq
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-49225
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.4, Vvveb backend product revision operations allow a low-privileged Vendor to access revisions for products owned by another Vendor. The admin/controller/product/revisions.php route reuses admin/controller/content/revisions.php, while admin/sql/sqlite/product_content_revision.sql trusts caller-controlled product_id, language_id, and created_at values without applying the current admin_id to revision reads, restores, and deletes. An attacker can read historic product content, restore a revision over another Vendor's live product content, or delete revision records, exposing private copy, corrupting product pages, and removing audit history. This issue is fixed in version 1.0.8.4.

## References
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49225.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-gmrp-ccwf-xggq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49225
- https://github.com/givanz/Vvveb/commit/e7413a29dcf1ccd04bbc44ebe26f20979223de14
