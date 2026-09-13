# [M] Ghidra < 12.1.3 PDB Parser Uncontrolled Heap Growth DoS via AbstractPdb

## Summary
Severity: Medium
Advisory: CVE-2026-54389
Aliases: GHSA-f75p-8cqj-9v3g
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-54389
Type: osv

## Details
Ghidra before 12.1.3 contains an uncontrolled resource consumption vulnerability in the PDB parser that allows attackers to terminate the Ghidra process by supplying a crafted PDB file with an oversized parameters section. The AbstractPdb deserialization routine reads all remaining parameters into an unbounded list, causing uncontrolled heap growth that triggers an OutOfMemoryError which bypasses exception handling and crashes the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54389.json
- https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.3_build
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-f75p-8cqj-9v3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-54389
- https://github.com/NationalSecurityAgency/ghidra
