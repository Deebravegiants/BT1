# [H] Spacebar Server Missing Authorization via Group DM Recipient Endpoint

## Summary
Severity: High
Advisory: CVE-2026-70617
Aliases: GHSA-g38j-78fh-jm74
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70617
Type: osv

## Details
Spacebar Server before commit dcfd910 contains a missing authorization vulnerability that allows any authenticated attacker to add themselves to arbitrary group DM channels by sending a PUT request to the channels recipient endpoint without membership verification. Attackers can exploit the unguarded PUT /channels/{channel_id}/recipients/{user_id} handler to join private group DMs, read complete message history, post messages as a participant, and force-add third-party users without their consent.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70617.json
- https://github.com/spacebarchat/server/security/advisories/GHSA-g38j-78fh-jm74
- https://nvd.nist.gov/vuln/detail/CVE-2026-70617
- https://www.vulncheck.com/advisories/spacebar-server-missing-authorization-via-group-dm-recipient-endpoint
- https://github.com/spacebarchat/server/commit/dcfd91035e3da42abf5f32d8d86a35219225b3d4
- https://github.com/spacebarchat/server
