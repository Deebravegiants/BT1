# [C] DeepTutor < 1.4.10 - Insecure Default Grants Unrestricted MCP Tool Access to Non-Admin Users

## Summary
Severity: Critical
Advisory: CVE-2026-58168
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58168
Type: osv

## Details
DeepTutor before version 1.4.10 contains an authorization bypass vulnerability that allows low-privilege users to invoke unrestricted MCP tools due to the allowed_mcp_tools function returning None instead of a denied result when mcp_tools is omitted from a user's grant in deeptutor/multi_user/tool_access.py. Attackers or prompt-injected content acting within a user session can enumerate and invoke any configured MCP tool, including filesystem, shell, and browser servers, gaining unauthorized access to sensitive deployment resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58168.json
- https://github.com/HKUDS/DeepTutor/releases/tag/v1.4.10
- https://nvd.nist.gov/vuln/detail/CVE-2026-58168
- https://www.vulncheck.com/advisories/deeptutor-insecure-default-grants-unrestricted-mcp-tool-access-to-non-admin-users
- https://github.com/HKUDS/DeepTutor/pull/579
- https://github.com/HKUDS/DeepTutor/commit/90046374b3dcd4f8a866d2d64a64440bc08eb2ef
- https://github.com/HKUDS/DeepTutor
