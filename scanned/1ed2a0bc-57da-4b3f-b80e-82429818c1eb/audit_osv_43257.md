# [M] Rocket.Chat: Insecure implementation of websocket notifications

## Summary
Severity: Medium
Advisory: CVE-2026-72918
Aliases: GHSA-27jx-236m-3f5j
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72918
Type: osv

## Details
Rocket.Chat is an open-source, secure, fully customizable communications platform. Prior to 7.10.14, 8.0.8, 8.1.7, 8.2.7, 8.3.7, 8.4.5, 8.5.2, and 8.6.1, the stream-notify-user stream in the WebSocket protocol allows an authenticated user to write arbitrary notification bodies because the sender is not checked, and the client-side UI can create an ephemeral fake message in another user's currently open chat. This issue is fixed in versions 7.10.14, 8.0.8, 8.1.7, 8.2.7, 8.3.7, 8.4.5, 8.5.2, and 8.6.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72918.json
- https://github.com/RocketChat/Rocket.Chat/security/advisories/GHSA-27jx-236m-3f5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-72918
