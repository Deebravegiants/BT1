# [H] Potential Insecure Direct Object Reference (IDOR) vulnerability in ragflow

## Summary
Severity: High
Advisory: CVE-2025-25282
Aliases: GHSA-wc5v-g79p-7hch
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-02-21
Source: https://osv.dev/vulnerability/CVE-2025-25282
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine based on deep document understanding. An authenticated user can exploit the Insecure Direct Object Reference (IDOR) vulnerability that may lead to unauthorized cross-tenant access (list tenant user accounts, add user account into other tenant). Unauthorized cross-tenant access: list user from other tenant (e.g., via GET /<tenant_id>/user/list), add user account to other tenant (POST /<tenant_id>/user). This issue has not yet been patched. Users are advised to reach out to the project maintainers to coordinate a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25282.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-wc5v-g79p-7hch
- https://nvd.nist.gov/vuln/detail/CVE-2025-25282
