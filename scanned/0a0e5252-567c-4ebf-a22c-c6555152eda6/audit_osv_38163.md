# [C] Anthropic Claude Code & Agent SDK OS Command Injection via TERMINAL Environment Variable

## Summary
Severity: Critical
Advisory: CVE-2026-35020
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35020
Type: osv

## Details
Anthropic Claude Code CLI and Claude Agent SDK contain an OS command injection vulnerability in the command lookup helper and deep-link terminal launcher that allows local attackers to execute arbitrary commands by manipulating the TERMINAL environment variable. Attackers can inject shell metacharacters into the TERMINAL variable which are interpreted by /bin/sh when the command lookup helper constructs and executes shell commands with shell=true. The vulnerability can be triggered during normal CLI execution as well as via the deep-link handler path, resulting in arbitrary command execution with the privileges of the user running the CLI.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35020.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35020
- https://www.vulncheck.com/advisories/anthropic-claude-code-agent-sdk-os-command-injection-via-terminal-environment-variable
- https://github.com/anthropics/claude-agent-sdk-python
- https://github.com/anthropics/claude-code
- https://phoenix.security/critical-ci-cd-nightmare-3-command-injection-flaws-in-claude-code-cli-allow-credential-exfiltration/
