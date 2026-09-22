# [M] Boards plugin retains Board Admin rights for users demoted to System Guest

## Summary
Severity: Medium
Advisory: CVE-2026-10527
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-10527
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21, 11.8.x <= 11.8.3 fails to reconcile SchemeAdmin flags with a user's current role which allows a user demoted to System Guest to retain Board Admin privileges and perform admin-only operations via the Boards REST API or UI.. Mattermost Advisory ID: MMSA-2026-00691

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10527.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10527
