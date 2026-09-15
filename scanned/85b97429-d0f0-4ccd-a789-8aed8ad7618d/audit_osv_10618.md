# [M] CVE-2017-17810

## Summary
Severity: Medium
Advisory: CVE-2017-17810
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17810
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there is a "SEGV on unknown address" that will cause a remote denial of service attack, because asm/preproc.c mishandles macro calls that have the wrong number of arguments.

## References
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392431
- http://repo.or.cz/nasm.git/commit/59ce1c67b16967c652765e62aa130b7e43f21dd4
