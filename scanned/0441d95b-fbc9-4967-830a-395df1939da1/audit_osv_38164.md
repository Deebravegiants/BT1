# [C] Anthropic Claude Code & Agent SDK OS Command Injection via Authentication Helper

## Summary
Severity: Critical
Advisory: CVE-2026-35022
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35022
Type: osv

## Details
Anthropic Claude Code CLI and Claude Agent SDK contain an OS command injection vulnerability in authentication helper execution where helper configuration values are executed using shell=true without input validation. Attackers who can influence authentication settings can inject shell metacharacters through parameters like apiKeyHelper, awsAuthRefresh, awsCredentialExport, and gcpAuthRefresh to execute arbitrary commands with the privileges of the user or automation environment, enabling credential theft and environment variable exfiltration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35022.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35022
- https://www.vulncheck.com/advisories/anthropic-claude-code-agent-sdk-os-command-injection-via-authentication-helper
- https://github.com/anthropics/claude-agent-sdk-python
- https://github.com/anthropics/claude-code
- https://phoenix.security/critical-ci-cd-nightmare-3-command-injection-flaws-in-claude-code-cli-allow-credential-exfiltration/
