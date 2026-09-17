# [M] LobeChat 2.2.9 - Cross-User Document Disclosure via Unscoped RAG Semantic Search

## Summary
Severity: Medium
Advisory: CVE-2026-59098
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-59098
Type: osv

## Details
LobeChat through 2.2.9 contains a broken access control vulnerability in the retrieval-augmented-generation semantic search functionality that allows authenticated attackers to access other users' data by exploiting missing user-identifier predicates in the chunk model semanticSearch method. Attackers can supply arbitrary victim file or knowledge-base identifiers through the chunk retrieval and chat knowledge-base paths to retrieve text content, file names, and metadata belonging to other users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59098.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59098
- https://www.vulncheck.com/advisories/lobechat-cross-user-document-disclosure-via-unscoped-rag-semantic-search
- https://github.com/lobehub/lobehub/pull/16594
- https://github.com/lobehub/lobehub/commit/4a7931a4e66832947dba11afdffae2918a56b6a0
- https://github.com/lobehub/lobehub
- https://github.com/lobehub/lobehub/issues/16535
