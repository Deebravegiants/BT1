# [H] InvenTree has Arbitrary API Token Creation

## Summary
Severity: High
Advisory: CVE-2026-35478
Aliases: GHSA-qh5j-c28q-c4rg
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35478
Type: osv

## Details
InvenTree is an Open Source Inventory Management System. From 0.16.0 to before 1.2.7, any authenticated InvenTree user can create a valid API token attributed to any other user in the system — including administrators and superusers — by supplying the target's user ID in the user field of a POST /api/user/tokens/ request. The returned token is immediately usable for full API authentication as the target user, from any network location, with no further interaction required. This vulnerability is fixed in 1.2.7 and 1.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35478.json
- https://github.com/inventree/InvenTree/security/advisories/GHSA-qh5j-c28q-c4rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35478
