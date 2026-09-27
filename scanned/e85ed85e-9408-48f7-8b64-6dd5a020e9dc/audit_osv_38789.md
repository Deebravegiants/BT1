# [M] Onyx: IDOR in /chat/stop-chat-session allows any authenticated user to interrupt other users chat sessions

## Summary
Severity: Medium
Advisory: CVE-2026-42276
Aliases: GHSA-rw6w-hp62-gc8w
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42276
Type: osv

## Details
Onyx is an open-source AI platform. Prior to versions 3.0.9, 3.1.6, and 3.2.6, the POST /chat/stop-chat-session/{chat_session_id} endpoint lets any authenticated user stop any other user's active chat session. The endpoint checks authentication but never verifies the session belongs to the caller. An attacker who knows a chat session UUID can kill another user's LLM generation mid-stream. This issue has been patched in versions 3.0.9, 3.1.6, and 3.2.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42276.json
- https://github.com/onyx-dot-app/onyx/security/advisories/GHSA-rw6w-hp62-gc8w
- https://nvd.nist.gov/vuln/detail/CVE-2026-42276
