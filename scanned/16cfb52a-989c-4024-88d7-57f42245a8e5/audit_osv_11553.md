# [M] CVE-2017-8421

## Summary
Severity: Medium
Advisory: CVE-2017-8421
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-02
Source: https://osv.dev/vulnerability/CVE-2017-8421
Type: osv

## Details
The function coff_set_alignment_hook in coffcode.h in Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, has a memory leak vulnerability which can cause memory exhaustion in objdump via a crafted PE file. Additional validation in dump_relocs_in_section in objdump.c can resolve this.

## References
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21440
