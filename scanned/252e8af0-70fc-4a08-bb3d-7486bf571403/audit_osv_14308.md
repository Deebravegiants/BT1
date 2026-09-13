# [H] CVE-2018-8882

## Summary
Severity: High
Advisory: CVE-2018-8882
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/CVE-2018-8882
Type: osv

## Details
Netwide Assembler (NASM) 2.13.02rc2 has a stack-based buffer under-read in the function ieee_shr in asm/float.c via a large shift value.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://bugzilla.nasm.us/show_bug.cgi?id=3392445
