# [M] CVE-2025-69652

## Summary
Severity: Medium
Advisory: CVE-2025-69652
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2025-69652
Type: osv

## Details
GNU Binutils thru 2.46 readelf contains a vulnerability that leads to an abort (SIGABRT) when processing a crafted ELF binary with malformed DWARF abbrev or debug information. Due to incomplete state cleanup in process_debug_info(), an invalid debug_info_p state may propagate into DWARF attribute parsing routines. When certain malformed attributes result in an unexpected data length of zero, byte_get_little_endian() triggers a fatal abort. No evidence of memory corruption or code execution was observed; the impact is limited to denial of service.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=44b79abd0fa12e7947252eb4c6e5d16ed6033e01
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69652.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69652
- https://sourceware.org/bugzilla/show_bug.cgi?id=33701
