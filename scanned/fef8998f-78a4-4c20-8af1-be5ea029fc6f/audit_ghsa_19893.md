# [H] AgentScope arbitrary file download vulnerability in rpc_agent_client

## Summary
Severity: High
Advisory: GHSA-p6h7-hfj2-vmcf
CVE: CVE-2024-8501
CWE: CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-p6h7-hfj2-vmcf
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
An arbitrary file download vulnerability exists in the rpc_agent_client component of modelscope/agentscope version v0.0.4. This vulnerability allows any user to download any file from the rpc_agent's host by exploiting the download_file method. This can lead to unauthorized access to sensitive information, including configuration files, credentials, and potentially system files, which may facilitate further exploitation such as privilege escalation or lateral movement within the network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8501
- https://github.com/modelscope/agentscope
- https://github.com/pypa/advisory-database/tree/main/vulns/agentscope/PYSEC-2025-82.yaml
- https://huntr.com/bounties/83e433c0-ed2d-4b10-8358-d3c1eee0a47c
