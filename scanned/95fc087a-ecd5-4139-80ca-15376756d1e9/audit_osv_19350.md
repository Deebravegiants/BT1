# [M] CVE-2021-20284

## Summary
Severity: Medium
Advisory: CVE-2021-20284
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-20284
Type: osv

## Details
A flaw was found in GNU Binutils 2.35.1, where there is a heap-based buffer overflow in _bfd_elf_slurp_secondary_reloc_section in elf.c due to the number of symbols not calculated correctly. The highest threat from this vulnerability is to system availability.

## References
- https://security.gentoo.org/glsa/202208-30
- https://security.netapp.com/advisory/ntap-20210521-0010/
- https://bugzilla.redhat.com/show_bug.cgi?id=1937784
- https://sourceware.org/bugzilla/show_bug.cgi?id=26931
