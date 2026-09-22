# [H] CVE-2017-8397

## Summary
Severity: High
Advisory: CVE-2017-8397
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8397
Type: osv

## Details
The Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to an invalid read of size 1 and an invalid write of size 1 during processing of a corrupt binary containing reloc(s) with negative addresses. This vulnerability causes programs that conduct an analysis of binary programs using the libbfd library, such as objdump, to crash.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21434
