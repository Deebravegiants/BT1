# [H] Claude Code: Sandbox Escape via Symlink Following Allows Arbitrary File Write Outside Workspace

## Summary
Severity: High
Advisory: GHSA-vp62-r36r-9xqp
CVE: CVE-2026-39861
CWE: CWE-22, CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-vp62-r36r-9xqp
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.1.64

## Details
Claude Code's sandbox did not prevent sandboxed processes from creating symlinks pointing to locations outside the workspace. When Claude Code subsequently wrote to a path within such a symlink, its unsandboxed process followed the symlink and wrote to the target location outside the workspace without prompting the user for confirmation. This allowed a sandbox escape where neither the sandboxed command nor the unsandboxed app could independently write outside the workspace, but their combination could write to arbitrary locations, potentially leading to code execution outside the sandbox. Reliably exploiting this required the ability to add untrusted content into a Claude Code context window to trigger sandboxed code execution via prompt injection.

Users on standard Claude Code auto-update have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Claude Code thanks hackerone.com/philts for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-vp62-r36r-9xqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-39861
- https://github.com/anthropics/claude-code
