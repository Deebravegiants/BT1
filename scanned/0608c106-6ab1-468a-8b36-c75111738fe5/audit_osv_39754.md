# [M] Quest Bot: Per-channel permission overwrite bypass in purge and slowmode commands.

## Summary
Severity: Medium
Advisory: CVE-2026-47195
Aliases: GHSA-2wf8-554w-hrj9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:L)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47195
Type: osv

## Details
Quest Bot is an opensource Discord Bot. Prior to version 1.1.6, the purge and slowmode commands check only guild-level permissions on the invoking member. They do not check the member’s effective permissions in the channel where the command is run. A user denied channel-level moderation permissions can still delete messages or change slowmode through the bot. This issue has been patched in version 1.1.6.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.1.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47195.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-2wf8-554w-hrj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-47195
