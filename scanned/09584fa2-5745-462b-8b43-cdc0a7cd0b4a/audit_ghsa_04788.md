# [M] Claude Code Action: Malicious MCP Server Configuration in PRs Enables Remote Code Execution and Secret Exfiltration

## Summary
Severity: Medium
Advisory: GHSA-8q5r-mmjf-575q
CVE: CVE-2026-47751
CWE: CWE-78, CWE-200
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:L/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-8q5r-mmjf-575q
Type: github-advisory

## Affected
- GitHub Actions: `anthropics/claude-code-action` — affected >=0 <1.0.74

## Details
Due to the combination of checking out PR head branches (attacker-controlled), reading `.mcp.json` from the working directory via default setting sources, and unconditionally enabling all project MCP servers via `enableAllProjectMcpServers`, it was possible for an attacker who opened a PR containing a malicious `.mcp.json` file to achieve arbitrary code execution on the GitHub Actions runner. This could lead to exfiltration of secrets available to the workflow (such as API keys and tokens) when a privileged user triggered the Claude action on the PR. Exploiting this required the ability to open a pull request against a repository using the claude-code-action and a privileged user or automatic trigger to invoke the action on that PR.

Users pinned to a vulnerable version of claude-code-action are advised to update to the latest version. Users referencing anthropics/claude-code-action@v1, anthropics/claude-code-action@beta, anthropics/claude-code-action@main, or other non-pinned tags will have received this fix already

Claude Code thanks hackerone.com/reptou for reporting this issue.

## References
- https://github.com/anthropics/claude-code-action/security/advisories/GHSA-8q5r-mmjf-575q
- https://nvd.nist.gov/vuln/detail/CVE-2026-47751
- https://github.com/anthropics/claude-code-action/pull/1066
- https://github.com/anthropics/claude-code-action/commit/9ddce40de8c1ab71fb6303a125fdad0968dc1312
- https://github.com/anthropics/claude-code-action
- https://github.com/anthropics/claude-code-action/releases/tag/v1.0.74
