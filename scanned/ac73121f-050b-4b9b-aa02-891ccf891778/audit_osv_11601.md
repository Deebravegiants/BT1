# [M] CVE-2017-9038

## Summary
Severity: Medium
Advisory: CVE-2017-9038
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9038
Type: osv

## Details
GNU Binutils 2.28 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file, related to the byte_get_little_endian function in elfcomm.c, the get_unwind_section_word function in readelf.c, and ARM unwind information that contains invalid word offsets.

## References
- http://www.securityfocus.com/bid/98589
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=f32ba72991d2406b21ab17edc234a2f3fa7fb23d
- https://security.gentoo.org/glsa/201709-02
- https://blogs.gentoo.org/ago/2017/05/12/binutils-multiple-crashes/
