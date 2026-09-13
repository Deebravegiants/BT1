# [C] CodeWhale before 0.8.64 Remote Code Execution via allow_shell

## Summary
Severity: Critical
Advisory: CVE-2026-75911
Aliases: GHSA-gx45-xrj5-g6c4
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75911
Type: osv

## Details
CodeWhale versions before 0.8.64 fail to properly validate the allow_shell configuration parameter from project config files, allowing attackers to enable arbitrary shell command execution by committing a malicious .codewhale/config.toml file to a repository. When a user clones and opens the repository in CodeWhale, the AI model gains access to exec_shell and task_shell tools, enabling execution of arbitrary shell commands on the victim's machine without explicit user consent.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75911.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-gx45-xrj5-g6c4
- https://nvd.nist.gov/vuln/detail/CVE-2026-75911
- https://www.vulncheck.com/advisories/codewhale-before-remote-code-execution-via-allow-shell
- https://github.com/Hmbown/CodeWhale/commit/43563356b98c6b993085554da82e77370160a31c
