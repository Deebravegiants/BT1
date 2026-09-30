# [C] Claude HUD 0.0.12 Arbitrary Command Execution via COMSPEC Environment Variable

## Summary
Severity: Critical
Advisory: CVE-2026-47092
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-47092
Type: osv

## Details
Claude HUD through 0.0.12, patched in commit 234d9aa, contains a command injection vulnerability that allows local attackers to execute arbitrary commands by manipulating the COMSPEC environment variable. Attackers can set COMSPEC to an arbitrary binary path before claude-hud performs its version check, causing execFile() to execute the attacker-supplied executable with cmd.exe arguments, resulting in arbitrary code execution on Windows systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47092.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47092
- https://www.vulncheck.com/advisories/claude-hud-arbitrary-command-execution-via-comspec-environment-variable
- https://github.com/jarrodwatts/claude-hud/issues/485
- https://github.com/jarrodwatts/claude-hud/pull/487
- https://github.com/jarrodwatts/claude-hud/commit/234d9aad919b51326a43bcf90b45ae35c23afc30
- https://github.com/jarrodwatts/claude-hud
