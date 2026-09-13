# [H]  Neo4j Cypher MCP server is vulnerable to DNS rebinding 

## Summary
Severity: High
Advisory: GHSA-vcqx-v2mg-7chx
CVE: CVE-2025-10193
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-vcqx-v2mg-7chx
Type: github-advisory

## Affected
- PyPI: `mcp-neo4j-cypher` — affected >=0.2.2 <0.4.0

## Details
### Impact
DNS rebinding vulnerability in Neo4j Cypher MCP server allows malicious websites to bypass Same-Origin Policy protections and execute unauthorised tool invocations against locally running Neo4j MCP instances.&nbsp;The attack relies on the user being enticed to visit a malicious website and spend sufficient time there for DNS rebinding to succeed.

### Patches
CORS Middleware added to Cypher MCP server v0.4.0 that blocks all web-based access by default.

### Workarounds
If you cannot upgrade to v0.4.0 and above, use stdio mode.

### References
[Vendor Advisory](https://neo4j.com/security/cve-2025-10193)
https://www.cve.org/CVERecord?id=CVE-2025-10193 

Credits
We want to publicly recognize the contribution of Evan Harris from [mcpsec.dev](https://mcpsec.dev/) for reporting this issue and following the responsible disclosure [policy](https://neo4j.com/trust-center/responsible-disclosure/).

## References
- https://github.com/neo4j-contrib/mcp-neo4j/security/advisories/GHSA-vcqx-v2mg-7chx
- https://nvd.nist.gov/vuln/detail/CVE-2025-10193
- https://github.com/neo4j-contrib/mcp-neo4j/pull/165
- https://github.com/neo4j-contrib/mcp-neo4j/commit/5b9fbdda6401668d7aa006daf7e644805c067c15
- https://github.com/neo4j-contrib/mcp-neo4j
- https://github.com/neo4j-contrib/mcp-neo4j/releases/tag/mcp-neo4j-cypher-v0.4.0
- https://neo4j.com/security/cve-2025-10193
