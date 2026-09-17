# [C] AgentScope path traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c4cc-w454-4634
CVE: CVE-2024-8537
CWE: CWE-22, CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-c4cc-w454-4634
Type: github-advisory

## Affected
- PyPI: `agentscope` — affected >=0

## Details
A path traversal vulnerability exists in the modelscope/agentscope application, affecting all versions. The vulnerability is present in the /delete-workflow endpoint, allowing an attacker to delete arbitrary files from the filesystem. This issue arises due to improper input validation, enabling the attacker to manipulate file paths and delete sensitive files outside of the intended directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8537
- https://github.com/modelscope/agentscope/pull/459
- https://github.com/modelscope/agentscope/commit/7d285e862f86fa1d96ed04c4cd40a5f1b8f9189a
- https://github.com/modelscope/agentscope
- https://github.com/modelscope/agentscope/blob/01530ee6a99c86426aab1be11ec3b3b86ca640ac/src/agentscope/studio/_app.py#L743
- https://huntr.com/bounties/eeb8aa4b-e6e5-465c-b0dd-aa97e3b7dc09
