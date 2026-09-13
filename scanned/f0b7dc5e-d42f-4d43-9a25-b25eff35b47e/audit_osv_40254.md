# [M] Ghidra < 12.0.3 - Out-of-Memory in Rust Symbol Demangler via Malformed Symbol

## Summary
Severity: Medium
Advisory: CVE-2026-52753
Aliases: GHSA-m94m-fqr3-x442
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-52753
Type: osv

## Details
Ghidra before 12.0.3 contains an out-of-memory vulnerability in the rust_demangle function that allocates unbounded output buffers without size limits. Attackers can craft malicious Rust symbol names in binaries to trigger exponential memory allocation, causing process crashes during binary analysis.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52753.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-m94m-fqr3-x442
- https://nvd.nist.gov/vuln/detail/CVE-2026-52753
- https://www.vulncheck.com/advisories/ghidra-out-of-memory-in-rust-symbol-demangler-via-malformed-symbol
- https://github.com/nationalsecurityagency/ghidra
