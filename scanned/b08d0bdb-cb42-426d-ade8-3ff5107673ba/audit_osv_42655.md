# [M] Spacebar Server Cross-Channel Message Deletion via Permission Check Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-69114
Aliases: GHSA-62g6-28hv-h6hc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-69114
Type: osv

## Details
Spacebar Server before commit 8d126f4 contains a cross-channel message deletion vulnerability in the single-delete and bulk-delete message handlers that fail to scope message queries to the requested channel. Authenticated users with MANAGE_MESSAGES permission in any controlled channel can delete arbitrary messages in other channels by routing delete requests through their own channel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69114.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69114
- https://www.vulncheck.com/advisories/spacebar-server-cross-channel-message-deletion-via-permission-check-bypass
- https://github.com/spacebarchat/server/commit/8d126f401914d68fa8a97f7e5986dcfcc42de9a8
- https://github.com/spacebarchat/server
- https://github.com/spacebarchat/server/issues/1685
- https://github.com/spacebarchat/server/security/advisories/GHSA-62g6-28hv-h6hc
