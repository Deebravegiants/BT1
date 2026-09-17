# [M] Incoming webhook user attribution via unvalidated webhook owner

## Summary
Severity: Medium
Advisory: CVE-2026-9708
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-9708
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to validate that an assigned incoming webhook user has access to the target team or channel, which allows a requester with webhook management permissions to create posts or direct messages attributed to another user via crafted incoming webhook configuration and payloads.. Mattermost Advisory ID: MMSA-2026-00683

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9708.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9708
