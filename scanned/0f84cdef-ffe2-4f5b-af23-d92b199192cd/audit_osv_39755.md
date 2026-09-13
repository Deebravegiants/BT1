# [M] Quest Bot: Empty automod rule causes every guild message to be deleted

## Summary
Severity: Medium
Advisory: CVE-2026-47196
Aliases: GHSA-fgwg-6px5-cxp5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47196
Type: osv

## Details
Quest Bot is an opensource Discord Bot. Prior to version 1.1.6, the automod add command trims user input but does not reject an empty result. Adding a rule containing only whitespace stores an empty word. The message listener later checks content.includes(""), which is always true, causing the bot to delete every non-bot guild message. This issue has been patched in version 1.1.6.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.1.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47196.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-fgwg-6px5-cxp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-47196
