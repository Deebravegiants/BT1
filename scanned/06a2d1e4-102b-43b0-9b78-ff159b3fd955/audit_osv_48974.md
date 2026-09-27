# [H] CVE-2018-19215

## Summary
Severity: High
Advisory: CVE-2018-19215
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19215
Type: osv

## Details
Netwide Assembler (NASM) 2.14rc16 has a heap-based buffer over-read in expand_mmac_params in asm/preproc.c for the special cases of the % and $ and ! characters.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- https://repo.or.cz/nasm.git/commit/4b5b737d4991578b1918303dc0fd9c9ab5c7ce4f
- https://bugzilla.nasm.us/show_bug.cgi?id=3392525
