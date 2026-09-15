# [C] Ghidra < 12.0.2 - Path Traversal in Extension Installer via ZIP Entry Names

## Summary
Severity: Critical
Advisory: CVE-2026-52752
Aliases: GHSA-jhc2-q7qf-9c25
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52752
Type: osv

## Details
Ghidra before 12.0.2 contains a path traversal vulnerability in the extension installer that fails to validate ZIP entry names during extraction. Attackers can craft malicious extensions with traversal sequences like ../ in filenames to write arbitrary files outside the intended directory, enabling code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52752.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-jhc2-q7qf-9c25
- https://nvd.nist.gov/vuln/detail/CVE-2026-52752
- https://www.vulncheck.com/advisories/ghidra-path-traversal-in-extension-installer-via-zip-entry-names
- https://github.com/nationalsecurityagency/ghidra
