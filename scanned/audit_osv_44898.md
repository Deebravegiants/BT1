# [M] Open WebUI: Any authenticated user can hang the server via message deletion in a cyclic chat tree

## Summary
Severity: Medium
Advisory: CVE-2026-88000
Aliases: GHSA-3cgp-3cqx-j8w2, PYSEC-2026-3877
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-88000
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.10.0 until 0.11.1, DELETE /api/v1/chats/{id}/messages/{message_id} used the chat-history deletion helper in backend/open_webui/models/chats.py to follow childrenIds without recording visited message identifiers. An authenticated user could store a cyclic chat tree and delete a message, causing a synchronous infinite loop on the server request loop that blocked every user's requests until the process was killed. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88000.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3cgp-3cqx-j8w2
- https://nvd.nist.gov/vuln/detail/CVE-2026-88000
- https://github.com/open-webui/open-webui/commit/b933292d63d12be3fd1416fe55519ddc7aa336bc
- https://github.com/open-webui/open-webui/pull/28035
