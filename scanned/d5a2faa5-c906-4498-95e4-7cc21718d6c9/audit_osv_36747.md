# [M] WeKan < 8.19 Read-only Board Roles Can Update Cards

## Summary
Severity: Medium
Advisory: CVE-2026-25565
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25565
Type: osv

## Details
WeKan versions prior to 8.19 contain an authorization vulnerability where certain card update API paths validate only board read access rather than requiring write permission. This can allow users with read-only roles to perform card updates that should require write access.

## References
- https://wekan.fi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25565.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25565
- https://www.vulncheck.com/advisories/wekan-read-only-board-roles-can-update-cards
- https://github.com/wekan/wekan/commit/181f837d8cbae96bdf9dcbd31beaa3653c2c0285
- https://github.com/wekan/wekan
