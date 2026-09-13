# [H] AutoGPT Platform Exposes Graph Execution Results via Authorization Gap

## Summary
Severity: High
Advisory: CVE-2025-53944
Aliases: GHSA-x77j-qg2x-fgg6
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-53944
Type: osv

## Details
AutoGPT is a platform that allows users to create, deploy, and manage continuous artificial intelligence agents. In v0.6.15 and below, the external API's get_graph_execution_results endpoint has an authorization bypass vulnerability. While it correctly validates user access to the graph_id, it fails to verify ownership of the graph_exec_id parameter, allowing authenticated users to access any execution results by providing arbitrary execution IDs. The internal API implements proper validation for both parameters. This is fixed in v0.6.16.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53944.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-x77j-qg2x-fgg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-53944
- https://github.com/Significant-Gravitas/AutoGPT/commit/309114a727baa2063357810d444e9a119f8dd7f6
