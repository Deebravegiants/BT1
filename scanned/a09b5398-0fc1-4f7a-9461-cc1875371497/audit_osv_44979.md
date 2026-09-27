# [M] Global session revocation does not invalidate active WebSocket connections

## Summary
Severity: Medium
Advisory: CVE-2026-9162
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-9162
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.0, 11.6.x <= 11.6.2, 11.5.x <= 11.5.5, 10.11.x <= 10.11.17 fail to invalidate cached authentication state for active WebSocket connections during global session revocation, which allows a user with an existing WebSocket connection to remain authenticated and continue receiving real-time events until the cached session expires or the client reconnects.. Mattermost Advisory ID: MMSA-2026-00664

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9162.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9162
