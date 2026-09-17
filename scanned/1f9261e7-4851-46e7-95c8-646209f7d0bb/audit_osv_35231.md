# [M] CVE-2025-69646

## Summary
Severity: Medium
Advisory: CVE-2025-69646
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2025-69646
Type: osv

## Details
Binutils objdump contains a denial-of-service vulnerability when processing a crafted binary with malformed DWARF debug_rnglists data. A logic error in the handling of the debug_rnglists header can cause objdump to repeatedly print the same warning message and fail to terminate, resulting in an unbounded logging loop until the process is interrupted. The issue was observed in binutils 2.44. A local attacker can exploit this vulnerability by supplying a malicious input file, leading to excessive CPU and I/O usage and preventing completion of the objdump analysis.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=598704a00cbac5e85c2bedd363357b5bf6fcee33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69646.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69646
- https://sourceware.org/bugzilla/show_bug.cgi?id=33638
