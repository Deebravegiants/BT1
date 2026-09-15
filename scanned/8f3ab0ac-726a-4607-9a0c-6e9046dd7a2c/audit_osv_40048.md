# [C] CodexBar < 0.32.0 Privilege Escalation via CLI Installer Temp File

## Summary
Severity: Critical
Advisory: CVE-2026-49134
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-49134
Type: osv

## Details
CodexBar prior to 0.32.0 contains a privilege escalation vulnerability in the CLI installer that allows local attackers to execute arbitrary commands as root by exploiting a race condition in temporary file handling. The installer creates a temporary file with mktemp, writes a privileged shell payload into it, and executes it with administrator privileges via bash, allowing a same-user local process to rewrite the installer body before the administrator prompt is approved, causing attacker-controlled commands to run as root.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49134.json
- https://github.com/steipete/CodexBar/releases/tag/v0.32.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-49134
- https://www.vulncheck.com/advisories/codexbar-privilege-escalation-via-cli-installer-temp-file
- https://github.com/steipete/CodexBar/pull/1222
- https://github.com/steipete/CodexBar/commit/dbc944d46cd4cf7877d1ca47c44556fe573b46e8
- https://github.com/steipete/CodexBar
