# [H] Kitty has a shell command injection

## Summary
Severity: High
Advisory: CVE-2026-42850
Aliases: GHSA-p64q-59hq-5q65
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-42850
Type: osv

## Details
Kitty is a cross-platform GPU based terminal. In versions prior to 0.47.0, it is possible to inject commands within the subshell through kitty error. A special escape code will make kitty return an error, this error is not escaped and will be correctly echoed back to the terminal with CRLF, as such it will be run by the shell in use. To exploit this bug, the victim must use a netcat or a similar program to connect to the attacker, or else listening for someone to connect. Once this condition is set, an attacker could pwn the computer of the victim using a special kitty's escape code that will run a command in the shell in use. Version 04.7.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42850.json
- https://github.com/kovidgoyal/kitty/security/advisories/GHSA-p64q-59hq-5q65
- https://nvd.nist.gov/vuln/detail/CVE-2026-42850
