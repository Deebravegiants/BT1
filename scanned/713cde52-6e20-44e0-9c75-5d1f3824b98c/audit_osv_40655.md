# [M] LibreChat: IDOR in Message Deletion — Incomplete Fix for CVE-2024-41703 Leaves deleteMessages() Without User Filter

## Summary
Severity: Medium
Advisory: CVE-2026-54029
Aliases: GHSA-8892-xj8q-59xc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54029
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, the DELETE /api/messages/:conversationId/:messageId endpoint allows any authenticated user to delete any other user's messages. The validateMessageReq middleware only validates that the conversationId belongs to the requesting user, but the handler calls deleteMessages({ messageId }) using only the messageId as the MongoDB filter — without adding a user constraint. An attacker provides their own valid conversationId (to pass validation) and the victim's messageId (to target deletion), resulting in permanent, irrecoverable message deletion. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54029.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-8892-xj8q-59xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-54029
