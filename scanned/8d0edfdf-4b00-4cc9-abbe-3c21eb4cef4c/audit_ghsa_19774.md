# [H] AgentScope Cross-Origin Resource Sharing (CORS) vulnerability

## Summary
Severity: High
Advisory: GHSA-75v5-6885-59f9
CVE: CVE-2024-8487
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-75v5-6885-59f9
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A Cross-Origin Resource Sharing (CORS) vulnerability exists in modelscope/agentscope version v0.0.4. The CORS configuration on the agentscope server does not properly restrict access to only trusted origins, allowing any external domain to make requests to the API. This can lead to unauthorized data access, information disclosure, and potential further exploitation, thereby compromising the integrity and confidentiality of the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8487
- https://github.com/modelscope/agentscope
- https://github.com/pypa/advisory-database/tree/main/vulns/agentscope/PYSEC-2025-81.yaml
- https://huntr.com/bounties/7aca7507-a94e-4e63-83a2-15648e5c4067
