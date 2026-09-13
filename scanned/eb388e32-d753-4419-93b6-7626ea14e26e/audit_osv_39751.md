# [H] Quest Bot: AutoMod removal can delete rules from another guild by global rule ID

## Summary
Severity: High
Advisory: CVE-2026-47189
Aliases: GHSA-6rv9-6p24-w955
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47189
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.5, the AutoMod remove flow looks up and deletes rules by global database ID without verifying that the rule belongs to the guild where the command is executed. A user can learn a victim guild’s AutoMod rule ID through autocomplete, then remove that rule from another guild where they have Manage Server. This issue has been patched in version 1.0.5.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47189.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-6rv9-6p24-w955
- https://nvd.nist.gov/vuln/detail/CVE-2026-47189
