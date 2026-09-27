# [M] QAnything 2.0.0 Unauthenticated Cross-User File Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-85671
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85671
Type: osv

## Details
QAnything 2.0.0 contains an authentication bypass vulnerability in the /api/local_doc_qa/get_file_base64 and /api/local_doc_qa/get_doc endpoints that allows unauthenticated attackers to access any uploaded file or document. Attackers can enumerate file identifiers through unauthenticated endpoints and retrieve base64-encoded files or parsed document chunks without ownership verification to disclose cross-tenant knowledge base content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85671.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85671
- https://www.vulncheck.com/advisories/qanything-2.0.0-unauthenticated-cross-user-file-disclosure
- https://github.com/netease-youdao/QAnything/issues/670
- https://github.com/netease-youdao/QAnything
- https://github.com/netease-youdao/QAnything/blob/v2.0.0/qanything_kernel/qanything_server/handler.py
