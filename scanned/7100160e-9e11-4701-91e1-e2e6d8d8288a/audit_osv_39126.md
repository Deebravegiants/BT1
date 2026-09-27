# [H] JunoClaw: plugin-shell shell-metacharacter injection via shell wrapper

## Summary
Severity: High
Advisory: CVE-2026-43990
Aliases: GHSA-gpvm-3chf-2649
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43990
Type: osv

## Details
JunoClaw is an agentic AI platform built on Juno Network. Prior to 0.x.y-security-1, plugin-shell's run_command wrapped every agent-supplied command in 'sh -c' / 'cmd /C' and passed the full argument string to the shell's parser, allowing shell metacharacters in agent-supplied arguments to be interpreted as command syntax. This vulnerability is fixed in 0.x.y-security-1.

## References
- https://github.com/Dragonmonk111/junoclaw/releases/tag/v0.x.y-security-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43990.json
- https://github.com/Dragonmonk111/junoclaw/security/advisories/GHSA-gpvm-3chf-2649
- https://nvd.nist.gov/vuln/detail/CVE-2026-43990
- https://github.com/Dragonmonk111/junoclaw/commit/2bc54f6
