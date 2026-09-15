# [H] Quivr Chat Endpoints Missing Ownership Validation

## Summary
Severity: High
Advisory: CVE-2026-82284
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82284
Type: osv

## Details
Quivr versions through 0.0.322 fail to validate chat ownership in the GET /chat/{chat_id}/history, DELETE /chat/{chat_id}, and POST /chat/{chat_id}/question/answer endpoints. Authenticated attackers can read other users' conversation histories including private knowledge base content, delete arbitrary chats, and inject fabricated messages into other users' conversations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82284.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82284
- https://www.vulncheck.com/advisories/quivr-chat-endpoints-missing-ownership-validation
- https://github.com/QuivrHQ/quivr/issues/3697
- https://github.com/QuivrHQ/quivr
- https://github.com/QuivrHQ/quivr/blob/v0.0.322/backend/api/quivr_api/modules/chat/controller/chat_routes.py
