# [C] Quest Bot: Manage Server users can configure AutoRole to grant Administrator to controlled joining accounts

## Summary
Severity: Critical
Advisory: CVE-2026-47169
Aliases: GHSA-8vgg-4hpx-7qfg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47169
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.3, a user with Manage Server / ManageGuild, but without Manage Roles or Administrator, can configure the bot’s AutoRole feature to assign an arbitrary role to new members. If the selected role has Administrator and is below the bot’s highest role, the attacker can join with a controlled account and receive full server admin. This issue has been patched in version 1.0.3.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47169.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-8vgg-4hpx-7qfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47169
