# [M] Missing per-channel team-scope check in ABAC access control policy unassign allows cross-team policy removal

## Summary
Severity: Medium
Advisory: CVE-2026-15754
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-15754
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 11.8.x <= 11.8.3 The access control policy unassign endpoint fails to re-validate that each target channel still belongs to the requesting admin's team, which allows an authenticated team administrator to remove ABAC (attribute-based access control) policy assignments from channels outside their team via the policy unassign API after a channel has been moved to another team.. Mattermost Advisory ID: MMSA-2026-00718

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15754.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-15754
