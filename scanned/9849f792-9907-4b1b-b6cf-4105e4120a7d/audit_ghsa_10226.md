# [M] Claude Code: Insecure System-Wide Configuration Loading Enables Local Privilege Escalation on Windows

## Summary
Severity: Medium
Advisory: GHSA-5cwg-9f6j-9jvx
CVE: CVE-2026-35603
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-5cwg-9f6j-9jvx
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <2.1.75

## Details
On Windows, Claude Code loaded system-wide default configuration from `C:\ProgramData\ClaudeCode\managed-settings.json` without validating directory ownership or access permissions. Because the `ProgramData` directory is writable by non-administrative users by default and the `ClaudeCode` subdirectory was not pre-created or access-restricted, a low-privileged local user could create this directory and place a malicious configuration file that would be automatically loaded for any user launching Claude Code on the same machine. Exploiting this would have required a shared multi-user Windows system and a victim user to launch Claude Code after the malicious configuration was placed.

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Thank you to hackerone.com/edbr for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-5cwg-9f6j-9jvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-35603
- https://github.com/anthropics/claude-code
