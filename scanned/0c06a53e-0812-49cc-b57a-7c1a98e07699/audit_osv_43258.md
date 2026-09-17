# [M] Rocket.Chat: Broken Access Control in channels.convertToTeam Allows Unauthorized Conversion of Public Channels into Teams

## Summary
Severity: Medium
Advisory: CVE-2026-72919
Aliases: GHSA-4mvx-9h2h-hmg3
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72919
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 7.10.14, 8.0.8, 8.1.7, 8.2.7, 8.3.7, 8.4.5, 8.5.2, and 8.6.1, the channels.convertToTeam REST endpoint allows an authenticated registered user with the create-team permission to convert an unrelated public channel by supplying channelName instead of channelId because the edit-room permission is checked only for channelId. This issue is fixed in versions 7.10.14, 8.0.8, 8.1.7, 8.2.7, 8.3.7, 8.4.5, 8.5.2, and 8.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72919.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-4mvx-9h2h-hmg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-72919
- https://github.com/RocketChat/Rocket.Chat/commit/175a19c4151f41910499ef37df54f58022276d12
- https://github.com/RocketChat/Rocket.Chat/pull/41206
