# [H] Capgo - RBAC Demotion Privilege Retention via Stale org_users.user_right

## Summary
Severity: High
Advisory: CVE-2026-56241
Aliases: GHSA-rvvc-rvxv-qcrh
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-12
Source: https://osv.dev/vulnerability/CVE-2026-56241
Type: osv

## Details
Capgo before 12.128.2 contains a privilege escalation vulnerability where demoted super_admin users retain access to delete_non_compliant_bundles and count_non_compliant_bundles RPCs due to stale org_users.user_right column not being cleared during role binding deletion. Attackers can exploit this by maintaining a previously granted super_admin role to enumerate and bulk delete non-compliant bundles across the entire organization indefinitely.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56241.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-rvvc-rvxv-qcrh
- https://nvd.nist.gov/vuln/detail/CVE-2026-56241
- https://www.vulncheck.com/advisories/capgo-rbac-demotion-privilege-retention-via-stale-org-users-user-right
