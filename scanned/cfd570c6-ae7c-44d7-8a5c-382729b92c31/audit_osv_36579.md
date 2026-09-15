# [M] AnythingLLM has key leak in `systemSettings.js`

## Summary
Severity: Medium
Advisory: CVE-2026-24477
Aliases: GHSA-gm94-qc2p-xcwf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-24477
Type: osv

## Details
AnythingLLM is an application that turns pieces of content into context that any LLM can use as references during chatting. If AnythingLLM prior to version 1.10.0 is configured to use Qdrant as the vector database with an API key, this QdrantApiKey could be exposed in plain text to unauthenticated users via the `/api/setup-complete` endpoint. Leakage of QdrantApiKey allows an unauthenticated attacker full read/write access to the Qdrant vector database instance used by AnythingLLM. Since Qdrant often stores the core knowledge base for RAG in AnythingLLM, this can lead to complete compromise of the semantic search / retrieval functionality and indirect leakage of confidential uploaded documents. Version 1.10.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24477.json
- https://github.com/Mintplex-Labs/anything-llm/security/advisories/GHSA-gm94-qc2p-xcwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24477
