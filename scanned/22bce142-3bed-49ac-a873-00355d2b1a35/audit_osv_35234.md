# [M] CVE-2025-69649

## Summary
Severity: Medium
Advisory: CVE-2025-69649
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2025-69649
Type: osv

## Details
GNU Binutils thru 2.46 readelf contains a null pointer dereference vulnerability when processing a crafted ELF binary with malformed header fields. During relocation processing, an invalid or null section pointer may be passed into display_relocations(), resulting in a segmentation fault (SIGSEGV) and abrupt termination. No evidence of memory corruption beyond the null pointer dereference, nor any possibility of code execution, was observed.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=66a3492ce68e1ae45b2489bd9a815c39ea5d7f66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69649.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69649
- https://sourceware.org/bugzilla/show_bug.cgi?id=33697
