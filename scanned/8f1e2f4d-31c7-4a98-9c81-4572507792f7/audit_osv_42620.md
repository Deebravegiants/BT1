# [C] hashcat through 7.1.2 Arbitrary File Write via Restore File Option Injection

## Summary
Severity: Critical
Advisory: CVE-2026-68766
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-68766
Type: osv

## Details
hashcat fails to restrict command-line options when parsing restore files, allowing attackers to inject output-redirecting options like --outfile and --potfile-path. Attackers can craft restore files with malicious options to append attacker-controlled content to arbitrary files, enabling code execution when targeting shell startup files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68766.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68766
- https://www.vulncheck.com/advisories/hashcat-through-arbitrary-file-write-via-restore-file-option-injection
- https://github.com/hashcat/hashcat/issues/4738
- https://github.com/hashcat/hashcat/commit/fcae69f2438ff8eae0dc8e206b78067a1e465ed4
- https://github.com/hashcat/hashcat
- https://github.com/hashcat/hashcat/blob/v7.1.2/src/restore.c#L365-L369
