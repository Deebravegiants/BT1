# [M] CodeWhale before 0.8.64 Argument Injection via git_blame

## Summary
Severity: Medium
Advisory: CVE-2026-75912
Aliases: GHSA-c6mw-8xh8-gpq6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75912
Type: osv

## Details
CodeWhale versions before 0.8.64 contain an argument injection vulnerability in the git_blame tool that allows attackers to read arbitrary files by injecting git options into the unvalidated rev parameter. Attackers can supply rev values like --contents=/path/to/file to exfiltrate sensitive files such as SSH keys and credentials through the tool output returned to the model.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75912.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-c6mw-8xh8-gpq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-75912
- https://www.vulncheck.com/advisories/codewhale-before-argument-injection-via-git-blame
- https://github.com/Hmbown/CodeWhale/commit/9a34b5034d29f05d1f28fa61b04719ca6a741020
