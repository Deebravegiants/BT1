# [C] RAGFlow SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-27135
Aliases: GHSA-3gqj-66qm-25jq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-27135
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine. Versions 0.15.1 and prior are vulnerable to SQL injection. The ExeSQL component extracts the SQL statement from the input and sends it directly to the database query. As of time of publication, no patched version is available.

## References
- https://github.com/infiniflow/ragflow/blob/v0.15.1/agent/component/exesql.py
- https://swizzky.notion.site/ragflow-exesql-150ca6df7c03806989cefde915cf8e42?pvs=4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27135.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-3gqj-66qm-25jq
- https://nvd.nist.gov/vuln/detail/CVE-2025-27135
- https://swizzky.notion.site/ragflow-exesql-150ca6df7c03806989cefde915cf8e42
