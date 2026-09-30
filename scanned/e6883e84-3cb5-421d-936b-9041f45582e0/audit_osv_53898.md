# [M] CVE-2023-31723

## Summary
Severity: Medium
Advisory: CVE-2023-31723
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-31723
Type: osv

## Details
yasm 1.3.0.55.g101bc was discovered to contain a segmentation violation via the function expand_mmac_params at /nasm/nasm-pp.c.

## References
- https://github.com/yasm/yasm/issues/220
- https://github.com/DaisyPo/fuzzing-vulncollect/blob/main/yasm/SEGV/nasm-pp.c:4008%20in%20expand_mmac_params/README.md
