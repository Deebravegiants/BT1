# [H] CVE-2018-19214

## Summary
Severity: High
Advisory: CVE-2018-19214
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19214
Type: osv

## Details
Netwide Assembler (NASM) 2.14rc15 has a heap-based buffer over-read in expand_mmac_params in asm/preproc.c for insufficient input.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00017.html
- https://bugzilla.nasm.us/show_bug.cgi?id=3392521
- https://repo.or.cz/nasm.git/commit/661f723d39e03ca6eb05d7376a43ca33db478354
