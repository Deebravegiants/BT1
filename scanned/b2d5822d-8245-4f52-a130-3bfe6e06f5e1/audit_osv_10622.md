# [M] CVE-2017-17814

## Summary
Severity: Medium
Advisory: CVE-2017-17814
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17814
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there is a use-after-free in do_directive in asm/preproc.c that will cause a remote denial of service attack.

## References
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392430
