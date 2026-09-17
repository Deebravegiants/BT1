# [H] Claude Code: Sandbox Escape via Git Worktree Path Confusion Allows Unsandboxed Code Execution

## Summary
Severity: High
Advisory: GHSA-7835-87q9-rgvv
CVE: CVE-2026-55607
CWE: CWE-22, CWE-59, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-7835-87q9-rgvv
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=2.1.38 <2.1.163

## Details
Claude Code's worktree handling allowed creation of worktrees named ".git" and navigation to worktrees outside the sandbox context, enabling git directory confusion attacks. By exploiting symlink manipulation and git fsmonitor execution during worktree operations, an attacker could overwrite files in the user's home directory (such as .zshenv), leading to code execution outside of seatbelt sandbox restrictions. Reliably exploiting this required the user to clone a malicious repository containing prompt injection content and run Claude Code against it.

Users on standard Claude Code auto-update have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Thank you to hackerone.com/metnew for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-7835-87q9-rgvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-55607
- https://github.com/anthropics/claude-code
- https://github.com/anthropics/claude-code/releases/tag/v2.1.163
