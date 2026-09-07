# [H] AgentScope directory traversal vulnerability in /read-examples

## Summary
Severity: High
Advisory: GHSA-6v28-q95m-93qr
CVE: CVE-2024-8524
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-6v28-q95m-93qr
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A directory traversal vulnerability exists in modelscope/agentscope version 0.0.4. An attacker can exploit this vulnerability to read any local JSON file by sending a crafted POST request to the /read-examples endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8524
- https://github.com/modelscope/agentscope
- https://github.com/modelscope/agentscope/blob/af8e45ded37b3834c981473b309239e0102473d0/src/agentscope/studio/_app.py#L642
- https://github.com/pypa/advisory-database/tree/main/vulns/agentscope/PYSEC-2025-83.yaml
- https://huntr.com/bounties/cc4acf33-700d-4220-8a8a-db28f5c4cc8f
