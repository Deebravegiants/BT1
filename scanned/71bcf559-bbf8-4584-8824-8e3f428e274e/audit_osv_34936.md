# [M] Nextcloud Deck app allowed user with "Can share" permission to modify permissions of other non-owners

## Summary
Severity: Medium
Advisory: CVE-2025-66557
Aliases: GHSA-wwr8-hx9g-rjvv
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66557
Type: osv

## Details
Nextcloud Deck is a kanban style organization tool aimed at personal planning and project organization for teams integrated with Nextcloud. Prior to 1.14.6 and 1.15.2, a bug in the permission logic allowed users with "Can share" permission to modify the permissions of other recipients. This vulnerability is fixed in 1.14.6 and 1.15.2.

## References
- https://hackerone.com/reports/3247499
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66557.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wwr8-hx9g-rjvv
- https://nvd.nist.gov/vuln/detail/CVE-2025-66557
- https://github.com/nextcloud/deck/commit/f1da8b30a455f02373d44154da04494c949a95ae
- https://github.com/nextcloud/deck/pull/7131
