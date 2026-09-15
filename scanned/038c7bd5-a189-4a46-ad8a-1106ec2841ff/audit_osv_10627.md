# [M] CVE-2017-17819

## Summary
Severity: Medium
Advisory: CVE-2017-17819
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17819
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there is an illegal address access in the function find_cc() in asm/preproc.c that will cause a remote denial of service attack, because pointers associated with skip_white_ calls are not validated.

## References
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392435
- http://repo.or.cz/nasm.git/commit/7524cfd91492e6e3719b959498be584a9ced13af
