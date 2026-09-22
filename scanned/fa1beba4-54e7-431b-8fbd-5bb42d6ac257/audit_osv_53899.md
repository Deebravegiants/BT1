# [H] CVE-2023-31724

## Summary
Severity: High
Advisory: CVE-2023-31724
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-31724
Type: osv

## Details
yasm 1.3.0.55.g101bc was discovered to contain a segmentation violation via the function do_directive at /nasm/nasm-pp.c.

## References
- https://github.com/yasm/yasm/issues/222
- https://github.com/DaisyPo/fuzzing-vulncollect/tree/main/yasm/SEGV/nasm-pp.c:3570%20in%20do_directive
