# [M] Server-Side Request Forgery in langchain-community.retrievers.web_research.WebResearchRetriever

## Summary
Severity: Medium
Advisory: GHSA-q25c-c977-4cmh
CVE: CVE-2024-3095
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-q25c-c977-4cmh
Type: github-advisory

## Affected
- PyPI: `langchain-community` — affected >=0 <0.2.9

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the Web Research Retriever component in langchain-community (langchain-community.retrievers.web_research.WebResearchRetriever). The vulnerability arises because the Web Research Retriever does not restrict requests to remote internet addresses, allowing it to reach local addresses. This flaw enables attackers to execute port scans, access local services, and in some scenarios, read instance metadata from cloud environments. The vulnerability is particularly concerning as it can be exploited to abuse the Web Explorer server as a proxy for web attacks on third parties and interact with servers in the local network, including reading their response data. This could potentially lead to arbitrary code execution, depending on the nature of the local services. The vulnerability is limited to GET requests, as POST requests are not possible, but the impact on confidentiality, integrity, and availability is significant due to the potential for stolen credentials and state-changing interactions with internal APIs.

The patched code:
* Requires users to opt-in
* Suggests using a proxy to prevent requests to local addresses

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3095
- https://github.com/langchain-ai/langchain/pull/24451
- https://github.com/langchain-ai/langchain/commit/604dfe2d99246b0c09f047c604f0c63eafba31e7
- https://github.com/langchain-ai/langchain
- https://github.com/langchain-ai/langchain/releases/tag/langchain-community%3D%3D0.2.9
- https://huntr.com/bounties/e62d4895-2901-405b-9559-38276b6a5273
