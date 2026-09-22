# [M] CVE-2018-10316

## Summary
Severity: Medium
Advisory: CVE-2018-10316
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2018-10316
Type: osv

## Details
Netwide Assembler (NASM) 2.14rc0 has an endless while loop in the assemble_file function of asm/nasm.c because of a globallineno integer overflow.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://bugzilla.nasm.us/show_bug.cgi?id=3392474
