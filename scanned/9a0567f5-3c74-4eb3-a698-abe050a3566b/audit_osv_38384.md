# [M] MaxKB: RCE via MCP stdio command injection in workflow engine

## Summary
Severity: Medium
Advisory: CVE-2026-39417
Aliases: GHSA-pw52-326g-r5xj
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-39417
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. Versions 2.7.1 and below contain an incomplete fix for CVE-2025-53928, where a Remote Code Execution vulnerability still exists in the MCP node of the workflow engine. MaxKB only restricts the referencing code path (loading MCP config from the database). The else branch, responsible for loading mcp_servers directly from user-supplied JSON remains completely unpatched. Since mcp_source is an optional field (required=False), an attacker can simply omit it or set it to any non-referencing value to bypass the fix. By calling the workflow creation API directly with a crafted JSON payload, an attacker can inject a complete MCP node configuration with stdio transport, arbitrary command, and args — achieving RCE when the workflow is triggered via chat. This issue has been fixed in version 2.8.0.

## References
- https://github.com/1Panel-dev/MaxKB/releases/tag/v2.8.0
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-pw52-326g-r5xj
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39417.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39417
- https://github.com/1Panel-dev/MaxKB/commit/50e96002ee5dca34c68d3d9333b64ea358c92304
