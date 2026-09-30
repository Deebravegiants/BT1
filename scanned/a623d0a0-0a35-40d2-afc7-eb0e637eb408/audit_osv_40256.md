# [C] Ghidra < 12.0.4 - Path Traversal via Zip Slip in Theme Import

## Summary
Severity: Critical
Advisory: CVE-2026-52755
Aliases: GHSA-3r55-xjr4-jh8f
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52755
Type: osv

## Details
Ghidra before 12.0.4 contains a path traversal vulnerability in the theme import functionality that allows attackers to write files outside the intended theme directory. Attackers can craft malicious theme ZIP files with traversal sequences in filenames to execute arbitrary code or modify sensitive files like .bashrc or .ssh/authorized_keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52755.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-3r55-xjr4-jh8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-52755
- https://www.vulncheck.com/advisories/ghidra-path-traversal-via-zip-slip-in-theme-import
- https://github.com/nationalsecurityagency/ghidra
