# [M] Ordinary group/direct message member can enable group_constrained and remove all channel participants

## Summary
Severity: Medium
Advisory: CVE-2026-10085
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-10085
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to restrict the group_constrained channel flag to public and private channels that support group synchronization, which allows an ordinary group or direct message member to remove all participants from the conversation via the channel patch API.. Mattermost Advisory ID: MMSA-2026-00688

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10085.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10085
