# [H] LangChain Community SSRF vulnerability exists in RequestsToolkit component 

## Summary
Severity: High
Advisory: GHSA-h5gc-rm8j-5gpr
CVE: CVE-2025-2828
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-23
Source: https://github.com/advisories/GHSA-h5gc-rm8j-5gpr
Type: github-advisory

## Affected
- PyPI: `langchain-community` — affected >=0 <0.0.28

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the RequestsToolkit component of the langchain-community package (specifically, langchain_community.agent_toolkits.openapi.toolkit.RequestsToolkit) in langchain-ai/langchain version 0.0.27. This vulnerability occurs because the toolkit does not enforce restrictions on requests to remote internet addresses, allowing it to also access local addresses. As a result, an attacker could exploit this flaw to perform port scans, access local services, retrieve instance metadata from cloud environments (e.g., Azure, AWS), and interact with servers on the local network. This issue has been fixed in version 0.0.28.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2828
- https://github.com/langchain-ai/langchain/commit/e188d4ecb085d4561a0be3c583d26aa9c2c3283f
- https://github.com/langchain-ai/langchain-community
- https://github.com/pypa/advisory-database/tree/main/vulns/langchain-community/PYSEC-2025-70.yaml
- https://huntr.com/bounties/8f771040-7f34-420a-b96b-5b93d4a99afc
