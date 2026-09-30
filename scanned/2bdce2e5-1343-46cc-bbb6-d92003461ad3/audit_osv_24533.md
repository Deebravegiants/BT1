# [M] Nextcloud Deck card vulnerable to data leak to unauthorized users via reference preview cache

## Summary
Severity: Medium
Advisory: CVE-2023-22469
Aliases: GHSA-8fjp-w9gp-j5hq
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2023-01-10
Source: https://osv.dev/vulnerability/CVE-2023-22469
Type: osv

## Details
Deck is a kanban style organization tool aimed at personal planning and project organization for teams integrated with Nextcloud. When getting the reference preview for Deck cards the user has no access to, unauthorized user could eventually get the cached data of a user that has access. There are currently no known workarounds. It is recommended that the Nextcloud app Deck is upgraded to 1.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22469.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8fjp-w9gp-j5hq
- https://nvd.nist.gov/vuln/detail/CVE-2023-22469
- https://github.com/nextcloud/deck/pull/4196
