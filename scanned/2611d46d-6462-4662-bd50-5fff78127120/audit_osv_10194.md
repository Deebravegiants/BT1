# [M] CVE-2017-14228

## Summary
Severity: Medium
Advisory: CVE-2017-14228
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/CVE-2017-14228
Type: osv

## Details
In Netwide Assembler (NASM) 2.14rc0, there is an illegal address access in the function paste_tokens() in preproc.c, aka a NULL pointer dereference. It will lead to remote denial of service.

## References
- https://security.gentoo.org/glsa/201903-19
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392423
