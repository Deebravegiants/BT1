# [M] CVE-2017-17815

## Summary
Severity: Medium
Advisory: CVE-2017-17815
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17815
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there is an illegal address access in is_mmacro() in asm/preproc.c that will cause a remote denial of service attack, because of a missing check for the relationship between minimum and maximum parameter counts.

## References
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392436
- http://repo.or.cz/nasm.git/commit/c9244eaadd05b27637cde06021bac3fa1d920aa3
