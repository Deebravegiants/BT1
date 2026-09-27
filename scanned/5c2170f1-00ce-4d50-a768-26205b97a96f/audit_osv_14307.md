# [H] CVE-2018-8881

## Summary
Severity: High
Advisory: CVE-2018-8881
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8881
Type: osv

## Details
Netwide Assembler (NASM) 2.13.02rc2 has a heap-based buffer over-read in the function tokenize in asm/preproc.c, related to an unterminated string.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://usn.ubuntu.com/3694-1/
- https://bugzilla.nasm.us/show_bug.cgi?id=3392446
