# [H] Vvveb post revision authorization bypass allows Authors to read, restore, or delete other Authors' post revisions

## Summary
Severity: High
Advisory: CVE-2026-49224
Aliases: GHSA-88w5-4x93-48rf
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-49224
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.4, Vvveb backend post revision operations allow a low-privileged Author to access revisions for posts owned by another Author. The admin/controller/content/revisions.php controller and admin/sql/sqlite/post_content_revision.sql queries trust caller-controlled post_id, language_id, and created_at values without consistently applying the current admin_id to revision lists, reads, restores, and deletes. An attacker can read historic post content, restore a revision over another Author's live post content, or delete revision records, exposing drafts, corrupting published content, and removing audit history. This issue is fixed in version 1.0.8.4.

## References
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49224.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-88w5-4x93-48rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-49224
- https://github.com/givanz/Vvveb/commit/cbedd3754bccf8b7584f02ab301291f12e888b7e
