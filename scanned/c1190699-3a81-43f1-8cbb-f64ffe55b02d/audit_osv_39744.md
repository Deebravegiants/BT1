# [M] Quest Bot: Reminder messages allow stored mass mentions through `@everyone` and `@here`

## Summary
Severity: Medium
Advisory: CVE-2026-47171
Aliases: GHSA-vmgg-f3m4-6fcv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47171
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.3, a normal user can create a reminder whose message contains @everyone or @here. When the reminder triggers, the bot sends the stored message back into the channel without suppressing mass mentions. If the bot has permission to mention everyone, the reminder can ping the entire server or channel later. This issue has been patched in version 1.0.3.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47171.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-vmgg-f3m4-6fcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-47171
