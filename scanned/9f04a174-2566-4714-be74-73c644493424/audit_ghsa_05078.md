# [M] @anthropic-ai/claude-code has an Insecure Temporary File in /copy Command that Enables Response Disclosure and Symlink-Based File Write

## Summary
Severity: Medium
Advisory: GHSA-4vp2-6q8c-pvq2
CVE: CVE-2026-46406
CWE: CWE-200, CWE-377, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-4vp2-6q8c-pvq2
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=2.1.59 <2.1.128

## Details
The Claude Code `/copy` command wrote responses to a hardcoded, predictable path (`/tmp/claude/response.md`) without UID isolation, randomness, or symlink protection. The file was created world-readable (0644) in a world-traversable directory (0755), allowing any local user to read a privileged user's Claude response, which could contain secrets or credentials. Additionally, because the path was static and predictable, a local attacker could pre-create the directory and plant a symlink at the expected file path, causing the privileged process to follow the symlink and overwrite an attacker-chosen file with the response text. Exploiting this required a local unprivileged user on the same system and a privileged user to run the `/copy` command.

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Claude Code thanks hackerone.com/c_h4ck_0 for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-4vp2-6q8c-pvq2
- https://github.com/anthropics/claude-code
