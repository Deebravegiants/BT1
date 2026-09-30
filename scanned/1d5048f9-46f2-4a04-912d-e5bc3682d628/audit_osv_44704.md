# [C] Blinko 1.8.7 Cross-User AI Conversation Read and Write via message tRPC Router

## Summary
Severity: Critical
Advisory: CVE-2026-85607
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85607
Type: osv

## Details
Blinko 1.8.7 contains an authorization bypass (IDOR) vulnerability in multiple tRPC procedures (message.list, message.update, message.delete, message.clearAfter in server/routerTrpc/message.ts and conversation.clearMessages in server/routerTrpc/conversation.ts). Although these procedures require authentication, they query the database by caller-supplied conversation or message ID without verifying that the resource belongs to the requesting account. Any authenticated user can therefore read another user's full AI chat history, modify individual message content, and delete or wipe entire conversations by enumerating sequential integer IDs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85607.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85607
- https://www.vulncheck.com/advisories/blinko-1.8.7-cross-user-ai-conversation-read-and-write-via-message-trpc-router
- https://github.com/blinkospace/blinko/issues/1218
- https://github.com/blinkospace/blinko
- https://github.com/blinkospace/blinko/blob/1.8.8/server/routerTrpc/conversation.ts
- https://github.com/blinkospace/blinko/blob/1.8.8/server/routerTrpc/message.ts
