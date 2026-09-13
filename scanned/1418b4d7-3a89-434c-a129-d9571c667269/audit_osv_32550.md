# [M] MaxKB has a reverse shell vulnerability in function library

## Summary
Severity: Medium
Advisory: CVE-2025-32383
Aliases: GHSA-fjf6-6cvf-xr72
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2025-32383
Type: osv

## Details
MaxKB (Max Knowledge Base) is an open source knowledge base question-answering system based on a large language model and retrieval-augmented generation (RAG). A reverse shell vulnerability exists in the module of function library. The vulnerability allow privileged‌ users to create a reverse shell. This vulnerability is fixed in v1.10.4-lts.

## References
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-fjf6-6cvf-xr72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32383.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32383
- https://github.com/1Panel-dev/MaxKB/commit/4ae02c8d3eb65542c88ef58c0abd94c52c949d8f
