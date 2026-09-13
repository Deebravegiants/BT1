# [M] LangChain's XMLOutputParser vulnerable to XML Entity Expansion

## Summary
Severity: Medium
Advisory: GHSA-q84m-rmw3-4382
CVE: CVE-2024-1455
CWE: CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-26
Source: https://github.com/advisories/GHSA-q84m-rmw3-4382
Type: github-advisory

## Affected
- PyPI: `langchain-core` — affected >=0 <0.1.35

## Details
The XMLOutputParser in LangChain uses the etree module from the XML parser in the standard python library which has some XML vulnerabilities; see: https://docs.python.org/3/library/xml.html

This primarily affects users that combine an LLM (or agent) with the `XMLOutputParser` and expose the component via an endpoint on a web-service. 

This would allow a malicious party to attempt to manipulate the LLM to produce a malicious payload for the parser that would compromise the availability of the service.

A successful attack is predicated on:

1. Usage of XMLOutputParser
2. Passing of malicious input into the XMLOutputParser either directly or by trying to manipulate an LLM to do so on the users behalf
3. Exposing the component via a web-service

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1455
- https://github.com/langchain-ai/langchain/pull/17250
- https://github.com/langchain-ai/langchain/pull/19653
- https://github.com/langchain-ai/langchain/pull/19660
- https://github.com/langchain-ai/langchain/commit/727d5023ce88e18e3074ef620a98137d26ff92a3
- https://github.com/langchain-ai/langchain
- https://huntr.com/bounties/4353571f-c70d-4bfd-ac08-3a89cecb45b6
