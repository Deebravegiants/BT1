# [H] Claude Code: Trust Dialog Bypass via Git Worktree Spoofing Allows Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-q5hj-mxqh-vv77
CVE: CVE-2026-40068
CWE: CWE-20, CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-q5hj-mxqh-vv77
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=2.1.63 <2.1.84

## Details
Claude Code used the git worktree `commondir` file when determining folder trust but did not validate its contents. By crafting a repository with a `commondir` file pointing to a path the victim had previously trusted, an attacker could bypass the trust dialog and immediately execute malicious hooks defined in `.claude/settings.json`. Exploiting this required the victim to clone a malicious repository and run Claude Code within it, and for the attacker to know or guess a path the victim had already trusted.

Users on standard Claude Code auto-update have received this fix already. Users performing manual updates are advised to update to the latest version.

Claude Code thanks [hackerone.com/masato_anzai](https://hackerone.com/masato_anzai) for reporting this issue.

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-q5hj-mxqh-vv77
- https://nvd.nist.gov/vuln/detail/CVE-2026-40068
- https://github.com/anthropics/claude-code
