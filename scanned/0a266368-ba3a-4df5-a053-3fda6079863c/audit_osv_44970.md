# [H] CVE-2026-9130

## Summary
Severity: High
Advisory: CVE-2026-9130
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-9130
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 contain an authorization bypass vulnerability in the MemoryComponent that allows authenticated users to access chat history of other users via session_id collision. The MemoryComponent.retrieve_messages and store_message methods filter on session_id without validating flow_id or user_id ownership, enabling cross-user information disclosure through multiple authenticated API endpoints including /api/v1/run/*, /api/v1/responses, and /api/v2/workflow/*. This vulnerability only affects multi-user deployments with LANGFLOW_AUTO_LOGIN=False.

## References
- https://www.ibm.com/support/pages/node/7282647
