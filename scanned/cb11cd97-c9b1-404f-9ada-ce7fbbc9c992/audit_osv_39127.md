# [H] JunoClaw: plugin-shell shell-injection bypass via substring blocklist

## Summary
Severity: High
Advisory: CVE-2026-43991
Aliases: GHSA-fvq5-79h6-952c
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43991
Type: osv

## Details
JunoClaw is an agentic AI platform built on Juno Network. Prior to 0.x.y-security-1, substring-based blocklist in plugin-shell's command-safety check could be bypassed by adversarial argument constructions, allowing unauthorized command execution on the host when combined with the companion advisory. Pre-patch, the check was applied to the raw command string rather than the parsed first token. This vulnerability is fixed in 0.x.y-security-1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43991.json
- https://github.com/Dragonmonk111/junoclaw/security/advisories/GHSA-fvq5-79h6-952c
- https://nvd.nist.gov/vuln/detail/CVE-2026-43991
- https://github.com/Dragonmonk111/junoclaw/commit/2bc54f6
