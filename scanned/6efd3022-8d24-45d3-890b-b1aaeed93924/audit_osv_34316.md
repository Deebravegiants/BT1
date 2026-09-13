# [C] LSTM-Kirigaya's openmcp-client Vulnerable to RCE in MCP Authorization Flow

## Summary
Severity: Critical
Advisory: CVE-2025-58062
Aliases: GHSA-43m4-p3rv-c4v8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-58062
Type: osv

## Details
LSTM-Kirigaya's openmcp-client is a vscode plugin for mcp developer. Prior to version 0.1.12, when users on a Windows platform connect to an attacker controlled MCP server, attackers could provision a malicious authorization server endpoint to silently achieve an OS command injection attack in the open() invocation, leading to client system compromise. This issue has been patched in version 0.1.12.

## References
- https://drive.google.com/file/d/1lSqFkc412aX6a_fjmNfzXsJKE7b8jPqD/view?usp=sharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58062.json
- https://github.com/LSTM-Kirigaya/openmcp-client/security/advisories/GHSA-43m4-p3rv-c4v8
- https://nvd.nist.gov/vuln/detail/CVE-2025-58062
- https://github.com/LSTM-Kirigaya/openmcp-client/commit/9c3799d6ffae8d0cdfab25a53af75e1afc85f6c3
