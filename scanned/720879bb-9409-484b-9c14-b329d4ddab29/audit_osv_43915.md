# [H] CodeWhale before 0.8.64 Argument Injection via git_show

## Summary
Severity: High
Advisory: CVE-2026-75913
Aliases: GHSA-7j5w-7r7x-9v27
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75913
Type: osv

## Details
CodeWhale (codewhale / codewhale-tui) versions >= 0.8.41 and < 0.8.64 contain an argument injection vulnerability in the git_show tool. The model-supplied rev parameter is passed unvalidated into the git show argv without an --end-of-options sentinel, so a value beginning with --output= is interpreted as a git flag. Because the tool is registered as auto-approved and advertised as read-only, an attacker (via a malicious repository combined with prompt injection) can cause an unprompted arbitrary file write at the privilege of the invoking user, targeting sensitive files such as ~/.ssh/authorized_keys, ~/.bashrc, or ~/.gitconfig. Fixed in 0.8.64 by adding rev validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75913.json
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-7j5w-7r7x-9v27
- https://nvd.nist.gov/vuln/detail/CVE-2026-75913
- https://www.vulncheck.com/advisories/codewhale-before-argument-injection-via-git-show
- https://github.com/Hmbown/CodeWhale/commit/9a34b5034d29f05d1f28fa61b04719ca6a741020
