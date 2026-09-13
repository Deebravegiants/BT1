# [C] Kitty vulnerable to command injection via unsanitized OSC 21 query reply

## Summary
Severity: Critical
Advisory: CVE-2026-54057
Aliases: GHSA-5gmr-9gwg-hhq6
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-54057
Type: osv

## Details
Kitty is a cross-platform GPU based terminal. In versions prior to 0.47.3, kitty's OSC 21 (color-control) query reply reflects attacker-controlled bytes, including newlines, into the shell's input without sanitization. Version 0.47.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54057.json
- https://github.com/kovidgoyal/kitty/security/advisories/GHSA-5gmr-9gwg-hhq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-54057
