# [M] Dify Has Broken Access Control on Log Message Endpoint Allows Reading of Chats of Others

## Summary
Severity: Medium
Advisory: CVE-2025-59422
Aliases: GHSA-jg5j-c9pq-w894
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-09-25
Source: https://osv.dev/vulnerability/CVE-2025-59422
Type: osv

## Details
Dify is an open-source LLM app development platform. In version 1.8.1, a broken access control vulnerability on the /console/api/apps/<APP_ID>chat-messages?conversation_id=<CONVERSATION_ID>&limit=10 endpoint allows users in the same workspace to read chat messages of other users. A regular user is able to read the query data and the filename of the admins and probably other users chats, if they know the conversation_id. This impacts the confidentiality of chats. This issue has been patched in version 1.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59422.json
- https://github.com/langgenius/dify/security/advisories/GHSA-jg5j-c9pq-w894
- https://nvd.nist.gov/vuln/detail/CVE-2025-59422
- https://github.com/langgenius/dify/commit/b2d8a7eaf1693841411934e2056042845ab4f354
