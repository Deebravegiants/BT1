# [H] Vvveb digital asset authorization bypass allows Vendors to list, read, edit, or delete other Vendors' digital assets

## Summary
Severity: High
Advisory: CVE-2026-49221
Aliases: GHSA-chpc-xj4m-9g3j
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-49221
Type: osv

## Details
Vvveb is a powerful and easy to use CMS with page builder to build websites, blogs or ecommerce stores. Prior to 1.0.8.4, Vvveb backend digital asset operations allow a low-privileged Vendor to access digital assets linked to another Vendor's products. The admin/controller/product/digital-asset.php and admin/controller/product/digital-assets.php controllers and the admin/sql/sqlite/digital_asset.sql data queries use a caller-controlled digital_asset_id without consistently enforcing the current admin_id ownership boundary. An attacker can list assets, read asset names and file metadata, edit asset metadata, or delete asset records, which can disclose private product metadata, corrupt resource links, and cause data loss. This issue is fixed in version 1.0.8.4.

## References
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49221.json
- https://github.com/givanz/Vvveb/security/advisories/GHSA-chpc-xj4m-9g3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-49221
- https://github.com/givanz/Vvveb/commit/0463ae60cda5085238b380bf53780ccf4be5dd50
