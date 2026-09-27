# [H] CVE-2017-14411

## Summary
Severity: High
Advisory: CVE-2017-14411
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14411
Type: osv

## Details
A stack-based buffer overflow was discovered in copy_mp in interface.c in mpglibDBL, as used in MP3Gain version 1.5.2. The vulnerability causes an out-of-bounds write, which leads to remote denial of service or possibly code execution.

## References
- https://blogs.gentoo.org/ago/2017/09/08/mp3gain-stack-based-buffer-overflow-in-copy_mp-mpglibdblinterface-c/
