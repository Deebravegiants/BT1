# [M] Quest Bot: Discord moderation role hierarchy bypass in ban, kick, mute, unmute, warn, and nickname commands

## Summary
Severity: Medium
Advisory: CVE-2026-47197
Aliases: GHSA-qw95-583r-hrwp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47197
Type: osv

## Details
Quest Bot is an opensource Discord Bot. Prior to version 1.1.6, a moderator with the relevant Discord permission bit can use the bot to moderate users above them in the Discord role hierarchy, as long as the bot itself outranks the target. This bypasses Discord’s normal role hierarchy protections and lets lower-ranked moderators ban, kick, timeout, untimeout, warn, or rename higher-ranked users. This issue has been patched in version 1.1.6.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.1.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47197.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-qw95-583r-hrwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47197
