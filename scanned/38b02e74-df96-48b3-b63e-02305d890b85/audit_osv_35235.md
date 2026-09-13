# [H] CVE-2025-69650

## Summary
Severity: High
Advisory: CVE-2025-69650
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2025-69650
Type: osv

## Details
GNU Binutils thru 2.46 readelf contains a double free vulnerability when processing a crafted ELF binary with malformed relocation data. During GOT relocation handling, dump_relocations may return early without initializing the all_relocations array. As a result, process_got_section_contents() may pass an uninitialized r_symbol pointer to free(), leading to a double free and terminating the program with SIGABRT. No evidence of exploitable memory corruption or code execution was observed; the impact is limited to denial of service. NOTE: this is disputed by third parties because the observed behavior occurred only in pre-release code and did not affect any tagged version.

## References
- https://sourceware.org/git/?p=binutils-gdb.git;a=commitdiff;h=81e90cf63a10ad11772c2437c8f2a88f1a00c739
- https://sourceware.org/git/?p=binutils-gdb.git;a=commitdiff;h=ea4bc025abdba85a90e26e13f551c16a44bfa92
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=ea4bc025abdba85a90e26e13f551c16a44bfa921
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69650.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69650
- https://sourceware.org/bugzilla/show_bug.cgi?id=33698
- https://sourceware.org/bugzilla/show_bug.cgi?id=33700
