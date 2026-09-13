# [H] AgentScope Path Traversal in /api/file

## Summary
Severity: High
Advisory: GHSA-f4hc-q562-cc5r
CVE: CVE-2024-8438
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-f4hc-q562-cc5r
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A path traversal vulnerability exists in modelscope/agentscope version v.0.0.4. The API endpoint `/api/file` does not properly sanitize the `path` parameter, allowing an attacker to read arbitrary files on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8438
- https://github.com/modelscope/agentscope
- https://github.com/modelscope/agentscope/blob/af8e45ded37b3834c981473b309239e0102473d0/src/agentscope/studio/_app.py#L578
- https://github.com/pypa/advisory-database/tree/main/vulns/agentscope/PYSEC-2025-80.yaml
- https://huntr.com/bounties/3f170c58-42ee-422d-ab6f-32c7aa05b974
