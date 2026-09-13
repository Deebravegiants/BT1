# [H] BigBlueButton vulnerable to Chat DoS via invalid reactionEmojiId

## Summary
Severity: High
Advisory: CVE-2025-61602
Aliases: GHSA-45j2-m26c-3pcm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-61602
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. A denial-of-service (DoS) vulnerability in versions prior to 3.0.13 allows any authenticated user to crash the chat functionality for all participants in a meeting by sending a malformed `reactionEmojiId` in the GraphQL mutation `chatSendMessageReaction`. Version 3.0.13 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61602.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-45j2-m26c-3pcm
- https://nvd.nist.gov/vuln/detail/CVE-2025-61602
- https://github.com/bigbluebutton/bigbluebutton/pull/23651
