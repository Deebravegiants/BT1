# [M] Denial of service in rocket chat message parser

## Summary
Severity: Medium
Advisory: GHSA-6375-pg5j-8wph
CVE: CVE-2024-46935
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-6375-pg5j-8wph
Type: github-advisory

## Affected
- npm: `@rocket.chat/message-parser` — affected >=0 <0.31.30

## Details
Rocket.Chat 6.12.0, 6.11.2, 6.10.5, 6.9.6, 6.8.6, 6.7.8, and earlier is vulnerable to denial of service (DoS). Attackers who craft messages with specific characters may crash the workspace due to an issue in the message parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46935
- https://github.com/RocketChat/Rocket.Chat/pull/33227
- https://docs.rocket.chat/docs/rocketchat-security-fixes-updates-and-advisories
- https://github.com/RocketChat/Rocket.Chat/releases/tag/6.12.1
- https://github.com/RocketChat/fuselage
