# [M] Quest Bot: Logging module can disclose private-channel message contents to a lower-visibility log channel

## Summary
Severity: Medium
Advisory: CVE-2026-47176
Aliases: GHSA-fvvp-8g5q-hrc7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47176
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.4, a user who can configure bot settings can enable logging and choose a logging channel they can read. The bot then logs deleted and edited message contents from every channel it can see, including private channels the configuring user cannot access. This issue has been patched in version 1.0.4.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47176.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-fvvp-8g5q-hrc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-47176
