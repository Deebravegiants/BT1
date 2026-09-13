# [C] Command Injection in nvm via NVM_AUTH_HEADER in wget code path

## Summary
Severity: Critical
Advisory: CVE-2026-1665
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-1665
Type: osv

## Details
A command injection vulnerability exists in nvm (Node Version Manager) versions 0.40.3 and below. The nvm_download() function uses eval to execute wget commands, and the NVM_AUTH_HEADER environment variable was not sanitized in the wget code path (though it was sanitized in the curl code path). An attacker who can set environment variables in a victim's shell environment (e.g., via malicious CI/CD configurations, compromised dotfiles, or Docker images) can inject arbitrary shell commands that execute when the victim runs nvm commands that trigger downloads, such as 'nvm install' or 'nvm ls-remote'.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1665.json
- https://github.com/nvm-sh/nvm/releases/tag/v0.40.4
- https://nvd.nist.gov/vuln/detail/CVE-2026-1665
- https://github.com/nvm-sh/nvm/commit/44e2590cdf257faf7d885e4470be8dc66cec9506
- https://github.com/nvm-sh/nvm/pull/3380
- https://github.com/nvm-sh/nvm
