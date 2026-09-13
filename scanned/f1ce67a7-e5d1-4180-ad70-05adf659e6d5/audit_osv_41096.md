# [M] Bitwarden Server < 2026.5.0 Privilege Escalation via Bulk User Remove Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-57520
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57520
Type: osv

## Details
Bitwarden Server before 2026.5.0 contains a privilege escalation vulnerability that allows authenticated Custom users with ManageUsers permission to remove Admin accounts from an organization by exploiting a missing role hierarchy check in the bulk user-remove endpoint. Attackers can supply Admin organization-user IDs in a bulk DELETE request to bypass the guard enforced on the single-user removal path, effectively removing one or more Admin accounts from an organization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57520.json
- https://github.com/bitwarden/server/releases/tag/v2026.5.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-57520
- https://www.vulncheck.com/advisories/bitwarden-server-privilege-escalation-via-bulk-user-remove-endpoint
- https://github.com/bitwarden/server/pull/7526
- https://github.com/bitwarden/server/commit/901bb67157c0f80d369c40b76742fdf7623da4e4
- https://github.com/bitwarden/server
- https://sanjokkarki.com.np/blog/bitwarden-bulk-remove-admin
