# [M] Saleor: Anonymous users can modify channel settings via `channelUpdate` due to `all([])` bypass in permission check

## Summary
Severity: Medium
Advisory: CVE-2026-48744
Aliases: GHSA-xqqq-qhgq-gx53
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-48744
Type: osv

## Details
Saleor is an e-commerce platform. From 3.14.67 until 3.21.67, 3.22.63, and 3.23.22, a broken authorization check in saleor/permission/utils.py can incorrectly authorize unauthenticated GraphQL requests. The flaw permits anonymous callers to use the channelUpdate() mutation to change channel order settings such as allowUnpaidOrders even when the response reports PermissionDenied. The same permission utility can expose hidden objects through the pageType() and translation() queries, including attributes whose visibleInStorefront field is false and that should be visible only to users with management permissions. This issue is fixed in versions 3.21.67, 3.22.63, and 3.23.22.

## References
- https://github.com/saleor/saleor/releases/tag/3.21.67
- https://github.com/saleor/saleor/releases/tag/3.22.63
- https://github.com/saleor/saleor/releases/tag/3.23.22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48744.json
- https://github.com/saleor/saleor/security/advisories/GHSA-xqqq-qhgq-gx53
- https://nvd.nist.gov/vuln/detail/CVE-2026-48744
- https://github.com/saleor/saleor/commit/11efb4e9ea76942cf142bc01de8846cbaf764465
- https://github.com/saleor/saleor/commit/580b93b6e0faef7800e667f0c3bc507d3ef6f5f5
- https://github.com/saleor/saleor/commit/9b1f59b3ed86c3fad3ce071639cf434c1ab94a85
- https://github.com/saleor/saleor/commit/afd1ddd13b79e78db4e05f846b1f159078c50417
