# [M] Unauthorized users can trigger interactive post actions in private channels via action cookie channel mismatch in Mattermost

## Summary
Severity: Medium
Advisory: CVE-2026-10106
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-10106
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to verify that the channel referenced in an action cookie matches the channel of the target post, which allows an authenticated user without access to a private channel to trigger interactive post actions on posts in that channel via a cookie obtained from any accessible channel.. Mattermost Advisory ID: MMSA-2026-00690

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10106.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10106
