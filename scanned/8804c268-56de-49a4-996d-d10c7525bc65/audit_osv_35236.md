# [M] CVE-2025-69651

## Summary
Severity: Medium
Advisory: CVE-2025-69651
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2025-69651
Type: osv

## Details
GNU Binutils thru 2.46 readelf contains a vulnerability that leads to an invalid pointer free when processing a crafted ELF binary with malformed relocation or symbol data. If dump_relocations returns early due to parsing errors, the internal all_relocations array may remain partially uninitialized. Later, process_got_section_contents() may attempt to free an invalid r_symbol pointer, triggering memory corruption checks in glibc and causing the program to terminate with SIGABRT. No evidence of further memory corruption or code execution was observed; the impact is limited to denial of service. NOTE: this is disputed by third parties because the observed behavior occurred only in pre-release code and did not affect any tagged version.

## References
- https://sourceware.org/git/?p=binutils-gdb.git;a=commitdiff;h=81e90cf63a10ad11772c2437c8f2a88f1a00c739
- https://sourceware.org/git/?p=binutils-gdb.git;a=commitdiff;h=ea4bc025abdba85a90e26e13f551c16a44bfa92
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=ea4bc025abdba85a90e26e13f551c16a44bfa921
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69651.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69651
- https://sourceware.org/bugzilla/show_bug.cgi?id=33698
- https://sourceware.org/bugzilla/show_bug.cgi?id=33700
