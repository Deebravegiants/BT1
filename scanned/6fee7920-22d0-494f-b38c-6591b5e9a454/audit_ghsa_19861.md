# [C] AgentScope Deserialization Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9w5h-67gf-xvv8
CVE: CVE-2024-8502
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-9w5h-67gf-xvv8
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A vulnerability in the RpcAgentServerLauncher class of modelscope/agentscope v0.0.6a3 allows for remote code execution (RCE) via deserialization of untrusted data using the dill library. The issue occurs in the AgentServerServicer.create_agent method, where serialized input is deserialized using dill.loads, enabling an attacker to execute arbitrary commands on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8502
- https://github.com/modelscope/agentscope
- https://huntr.com/bounties/7a42da2a-2ae5-442d-aff9-c9a3b47870eb
