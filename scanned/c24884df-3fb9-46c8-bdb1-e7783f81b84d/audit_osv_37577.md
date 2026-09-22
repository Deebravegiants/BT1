# [M] LibreChat's IDOR in SSE Stream Subscription Allows Reading Other Users' Chats

## Summary
Severity: Medium
Advisory: CVE-2026-31950
Aliases: GHSA-f6rf-vm44-wh5g
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-31950
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. In versions 0.8.2-rc2 through 0.8.2-rc3, the SSE streaming endpoint `/api/agents/chat/stream/:streamId` does not verify that the requesting user owns the stream. Any authenticated user who obtains or guesses a valid stream ID can subscribe and read another user's real-time chat content, including messages, AI responses, and tool invocations. Version 0.8.2 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31950.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-f6rf-vm44-wh5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-31950
