# [M] CVE-2025-69648

## Summary
Severity: Medium
Advisory: CVE-2025-69648
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2025-69648
Type: osv

## Details
GNU Binutils thru 2.45.1 readelf contains a denial-of-service vulnerability when processing a crafted binary with malformed DWARF .debug_rnglists data. A logic flaw in the DWARF parsing path causes readelf to repeatedly print the same warning message without making forward progress, resulting in a non-terminating output loop that requires manual interruption. No evidence of memory corruption or code execution was observed.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=598704a00cbac5e85c2bedd363357b5bf6fcee33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69648.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69648
- https://sourceware.org/bugzilla/show_bug.cgi?id=33641
