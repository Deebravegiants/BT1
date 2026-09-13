# [M] Quest Bot: Ticket transcripts can disclose private ticket contents to a lower-visibility channel

## Summary
Severity: Medium
Advisory: CVE-2026-47177
Aliases: GHSA-4rpv-95pj-6ccg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47177
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.4, a user who can configure bot settings can set the ticket transcript channel to a channel they can read. When tickets are closed, the bot exports the full ticket history and sends it to that configured transcript channel. This can expose private ticket messages to users who could not read the original ticket channel. This issue has been patched in version 1.0.4.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47177.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-4rpv-95pj-6ccg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47177
