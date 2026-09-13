# [C] radare2 Command Injection via DWARF Parameter Names

## Summary
Severity: Critical
Advisory: CVE-2026-40527
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40527
Type: osv

## Details
radare2 prior to commit bc5a890 contains a command injection vulnerability in the afsv/afsvj command path where crafted ELF binaries can embed malicious r2 command sequences as DWARF DW_TAG_formal_parameter names. Attackers can craft a binary with shell commands in DWARF parameter names that execute when radare2 analyzes the binary with aaa and subsequently runs afsvj, allowing arbitrary shell command execution through the unsanitized parameter interpolation in the pfq command string.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40527.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40527
- https://www.vulncheck.com/advisories/radare2-command-injection-via-dwarf-parameter-names
- https://github.com/radareorg/radare2/pull/25821
- https://github.com/radareorg/radare2/commit/bc5a89033db3ecb5b1f7bf681fc6ba4dcfc14683
- https://github.com/radareorg/radare2
