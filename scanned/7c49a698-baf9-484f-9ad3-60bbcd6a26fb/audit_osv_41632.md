# [M] Fail-open authorization in grav-plugin-flex-objects admin-next API: api.access user gets full CRUD on permission-less directories (requireFlexPermission missing else-deny)

## Summary
Severity: Medium
Advisory: CVE-2026-62670
Aliases: CVE-2026-62235, GHSA-23vq-365v-qcmh
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-62670
Type: osv

## Details
Grav Flex Objects Plugin allows you to build custom collections of objects. Prior to 1.4.3, the Grav Flex Objects Admin Next API requireFlexPermission() method in classes/Api/FlexApiController.php returns without denying access when a directory blueprint omits config.admin.permissions. An authenticated account with only api.access can use the index, show, create, update, delete, export, and media handlers for a permission-less directory even though the core admin.flex-object. authorization fallback would deny the same actions. This issue is fixed in version 1.4.3.

## References
- https://github.com/trilbymedia/grav-plugin-flex-objects/releases/tag/1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62670.json
- https://github.com/getgrav/grav/security/advisories/GHSA-23vq-365v-qcmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-62670
- https://github.com/trilbymedia/grav-plugin-flex-objects/commit/198d1a0eb7b94777a026ed0001d9a369d94c3002
