# [C] radare2 < 6.1.4 Command Injection via PDB Parser print_gvars()

## Summary
Severity: Critical
Advisory: CVE-2026-40499
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-40499
Type: osv

## Details
radare2 prior to version 6.1.4 contains a command injection vulnerability in the PDB parser's print_gvars() function that allows attackers to execute arbitrary commands by embedding a newline byte in the PE section header name field. Attackers can craft a malicious PDB file with specially crafted section names to inject r2 commands that are executed when the idp command processes the file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40499.json
- https://github.com/radareorg/radare2/releases/tag/6.1.4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40499
- https://www.vulncheck.com/advisories/radare2-command-injection-via-pdb-parser-print-gvars
- https://github.com/radareorg/radare2/issues/25752
- https://github.com/radareorg/radare2/commit/5590c87deeb7eb2a106fd7aab9ca88bfeebb7397
