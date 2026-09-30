# [H] CVE-2017-8398

## Summary
Severity: High
Advisory: CVE-2017-8398
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8398
Type: osv

## Details
dwarf.c in GNU Binutils 2.28 is vulnerable to an invalid read of size 1 during dumping of debug information from a corrupt binary. This vulnerability causes programs that conduct an analysis of binary programs, such as objdump and readelf, to crash.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21438
