# [H] CVE-2017-7300

## Summary
Severity: High
Advisory: CVE-2017-7300
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-7300
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, has an aout_link_add_symbols function in bfd/aoutx.h that is vulnerable to a heap-based buffer over-read (off-by-one) because of an incomplete check for invalid string offsets while loading symbols, leading to a GNU linker (ld) program crash.

## References
- http://www.securityfocus.com/bid/97219
- https://sourceware.org/bugzilla/show_bug.cgi?id=20909
