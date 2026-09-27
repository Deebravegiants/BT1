# [M] Vim has OS Command Injection in netrw

## Summary
Severity: Medium
Advisory: CVE-2026-28417
Aliases: GHSA-m3xh-9434-g336
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28417
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0073, an OS command injection vulnerability exists in the `netrw` standard plugin bundled with Vim. By inducing a user to open a crafted URL (e.g., using the `scp://` protocol handler), an attacker can execute arbitrary shell commands with the privileges of the Vim process. Version 9.2.0073 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/6
- https://github.com/vim/vim/releases/tag/v9.2.0073
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28417.json
- https://github.com/vim/vim/security/advisories/GHSA-m3xh-9434-g336
- https://nvd.nist.gov/vuln/detail/CVE-2026-28417
- https://github.com/vim/vim/commit/79348dbbc09332130f4c860
