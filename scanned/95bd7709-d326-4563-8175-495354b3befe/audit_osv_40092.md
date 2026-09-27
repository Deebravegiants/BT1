# [M] Ghidra 10.2 < 12.1 - Denial of Service via Circular Reference in Mach-O Export Trie Parser

## Summary
Severity: Medium
Advisory: CVE-2026-49495
Aliases: GHSA-wm33-9f68-3vjg
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-49495
Type: osv

## Details
Ghidra 10.2 before 12.1 contains an uncontrolled resource consumption vulnerability in ExportTrie.parseTrie() that lacks cycle detection when traversing Mach-O binary export tries. A crafted Mach-O binary with circular references in the export trie causes unbounded queue growth and exponential string concatenation, triggering OutOfMemoryError that crashes the entire JVM and loses all unsaved work.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49495.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-wm33-9f68-3vjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-49495
- https://www.vulncheck.com/advisories/ghidra-denial-of-service-via-circular-reference-in-mach-o-export-trie-parser
- https://github.com/nationalsecurityagency/ghidra
