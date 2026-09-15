# [H] CVE-2018-8769

## Summary
Severity: High
Advisory: CVE-2018-8769
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-18
Source: https://osv.dev/vulnerability/CVE-2018-8769
Type: osv

## Details
elfutils 0.170 has a buffer over-read in the ebl_dynamic_tag_name function of libebl/ebldynamictagname.c because SYMTAB_SHNDX is unsupported.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=22976
