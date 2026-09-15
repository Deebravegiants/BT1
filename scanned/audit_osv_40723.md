# [M] DiscordChatExporter: HTML attribute injection via unescaped emoji name in HTML export

## Summary
Severity: Medium
Advisory: CVE-2026-54681
Aliases: GHSA-r7qm-wg9p-pjfc
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-54681
Type: osv

## Details
DiscordChatExporter saves Discord chat logs to a file. Prior to 2.47.2, the VisitEmojiAsync method in DiscordChatExporter.Core/Exporting/HtmlMarkdownVisitor.cs interpolates emoji.Name into the alt attribute and emoji.Code into the title attribute without HTML entity encoding. This affects HTML exports regardless of the markdown setting. Discord's current custom emoji name validation normally excludes attribute-breaking characters, but tampered offline input, a relaxed upstream validation rule, or another future metadata source can inject an HTML attribute and execute script when a user opens the export. This issue is fixed in version 2.47.2.

## References
- https://github.com/Tyrrrz/DiscordChatExporter/releases/tag/2.47.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54681.json
- https://github.com/Tyrrrz/DiscordChatExporter/security/advisories/GHSA-r7qm-wg9p-pjfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54681
- https://github.com/Tyrrrz/DiscordChatExporter/commit/f4d1e630f7f27120c3be4320d92cc8b932e78688
- https://github.com/Tyrrrz/DiscordChatExporter/pull/1544
