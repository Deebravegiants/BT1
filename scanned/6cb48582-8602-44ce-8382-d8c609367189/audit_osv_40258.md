# [M] Ghidra < 12.1.1 - Denial of Service via Uncontrolled Memory Allocation in Mach-O Parser

## Summary
Severity: Medium
Advisory: CVE-2026-52759
Aliases: GHSA-v6c3-h9cp-3whf
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52759
Type: osv

## Details
Ghidra before 12.1.1 contains an uncontrolled memory allocation vulnerability in the Mach-O binary parser that allows attackers to cause denial of service. An attacker can supply a crafted Mach-O binary with an arbitrarily large ncmds load command count value, forcing the parser to allocate excessive heap memory without validating file size, crashing the Ghidra JVM.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52759.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-v6c3-h9cp-3whf
- https://nvd.nist.gov/vuln/detail/CVE-2026-52759
- https://www.vulncheck.com/advisories/ghidra-denial-of-service-via-uncontrolled-memory-allocation-in-mach-o-parser
