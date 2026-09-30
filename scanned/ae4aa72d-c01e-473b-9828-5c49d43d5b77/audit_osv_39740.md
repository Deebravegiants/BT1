# [H] Quest Bot: Unprivileged users can create and remove AutoMod rules.

## Summary
Severity: High
Advisory: CVE-2026-47163
Aliases: GHSA-rphh-4h68-qr3j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47163
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.1, any guild member who can invoke slash commands can use /automod add, /automod remove, and /automod list because the command has no Discord default permission requirement and no runtime moderator permission check. An attacker can add a rule matching common text and make the bot delete other users’ messages. This issue has been patched in version 1.0.1.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47163.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-rphh-4h68-qr3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-47163
