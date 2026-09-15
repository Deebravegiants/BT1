# [C] Ghidra < 12.1- Command Injection via URL Annotation Click

## Summary
Severity: Critical
Advisory: CVE-2026-52750
Aliases: GHSA-5c38-3rf3-gp75
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52750
Type: osv

## Details
Ghidra before 12.1 contains a command injection vulnerability in URL annotation handling on Windows where cmd.exe metacharacters are not properly escaped. Attackers can execute arbitrary commands under the Ghidra user's privileges by embedding malicious URLs in program comments that victims click.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52750.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-5c38-3rf3-gp75
- https://nvd.nist.gov/vuln/detail/CVE-2026-52750
- https://www.vulncheck.com/advisories/ghidra-command-injection-via-url-annotation-click
- https://github.com/nationalsecurityagency/ghidra
