# [H] Vvveb product question authorization bypass allows Vendors to read, approve, edit, or delete questions under other Vendors' products

## Summary
Severity: High
Advisory: CVE-2026-49222
Aliases: GHSA-cjhq-xqq3-6xv8
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-49222
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.4, Vvveb backend product question operations allow a low-privileged Vendor to manage questions under another Vendor's products. The admin/sql/sqlite/product_question.sql queries accept a caller-controlled product_question_id and do not verify product_question.product_id against product.admin_id for the current admin_id. An attacker can read pending question content and moderation data, change question status, edit question content, or delete questions, manipulating product Q&A visibility and integrity. This issue is fixed in version 1.0.8.4.

## References
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49222.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-cjhq-xqq3-6xv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-49222
- https://github.com/givanz/Vvveb/commit/1f2b117c1460818c9306a78f22c12f0b713886df
