# [H] Missing authorization in gin-vue-admin

## Summary
Severity: High
Advisory: CVE-2022-21660
Aliases: GHSA-xxvh-9c87-pqjx
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-02-09
Source: https://osv.dev/vulnerability/CVE-2022-21660
Type: osv

## Details
Gin-vue-admin is a backstage management system based on vue and gin. In versions prior to 2.4.7 low privilege users are able to modify higher privilege users. Authentication is missing on the `setUserInfo` function. Users are advised to update as soon as possible. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21660.json
- https://github.com/flipped-aurora/gin-vue-admin/security/advisories/GHSA-xxvh-9c87-pqjx
- https://nvd.nist.gov/vuln/detail/CVE-2022-21660
