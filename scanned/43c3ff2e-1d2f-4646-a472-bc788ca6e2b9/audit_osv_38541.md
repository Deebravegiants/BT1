# [C] radare2 < 6.1.4 Command Injection via PDB Parser Symbol Names

## Summary
Severity: Critical
Advisory: CVE-2026-40517
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-40517
Type: osv

## Details
radare2 prior to 6.1.4 contains a command injection vulnerability in the PDB parser's print_gvars() function that allows attackers to execute arbitrary commands by crafting a malicious PDB file with newline characters in symbol names. Attackers can inject arbitrary radare2 commands through unsanitized symbol name interpolation in the flag rename command, which are then executed when a user runs the idp command against the malicious PDB file, enabling arbitrary OS command execution through radare2's shell execution operator.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40517.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40517
- https://www.vulncheck.com/advisories/radare2-command-injection-via-pdb-parser-symbol-names
- https://github.com/radareorg/radare2/issues/25730
- https://github.com/radareorg/radare2/pull/25731
- https://blog.calif.io/p/mad-bugs-discovering-a-0-day-in-zero
