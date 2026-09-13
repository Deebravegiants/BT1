# [M] Ghidra < 12.1 - Heap-Use-After-Free in SleighBuilder::generatePointerAdd via Vector Reallocation

## Summary
Severity: Medium
Advisory: CVE-2026-49496
Aliases: GHSA-gqh9-2c72-wpjc
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-49496
Type: osv

## Details
Ghidra before 12.1 contains a heap-use-after-free vulnerability in SleighBuilder::generatePointerAdd caused by iterator invalidation when PcodeCacher::allocateInstruction reallocates the issued vector. Attackers can trigger memory corruption by decompiling malicious binaries through the public Sleigh::oneInstruction C++ API, affecting downstream SLEIGH library consumers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49496.json
- https://github.com/NationalSecurityAgency/ghidra/security/advisories/GHSA-gqh9-2c72-wpjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-49496
- https://www.vulncheck.com/advisories/ghidra-heap-use-after-free-in-sleighbuilder-generatepointeradd-via-vector-reallocation
- https://github.com/NationalSecurityAgency/ghidra/commit/8a3018d5efcb07d2ec40bacdd6063cb6f01c8edf
- https://github.com/nationalsecurityagency/ghidra
