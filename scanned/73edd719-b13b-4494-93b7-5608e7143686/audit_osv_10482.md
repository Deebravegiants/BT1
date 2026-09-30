# [H] CVE-2017-15996

## Summary
Severity: High
Advisory: CVE-2017-15996
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-29
Source: https://osv.dev/vulnerability/CVE-2017-15996
Type: osv

## Details
elfcomm.c in readelf in GNU Binutils 2.29 allows remote attackers to cause a denial of service (excessive memory allocation) or possibly have unspecified other impact via a crafted ELF file that triggers a "buffer overflow on fuzzed archive header," related to an uninitialized variable, an improper conditional jump, and the get_archive_member_name, process_archive_index_and_symbols, and setup_archive functions.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=d91f0b20e561e326ee91a09a76206257bde8438b
- http://www.securityfocus.com/bid/101608
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=22361
