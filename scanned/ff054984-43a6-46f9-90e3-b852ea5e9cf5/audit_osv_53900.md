# [M] CVE-2023-31725

## Summary
Severity: Medium
Advisory: CVE-2023-31725
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-17
Source: https://osv.dev/vulnerability/CVE-2023-31725
Type: osv

## Details
yasm 1.3.0.55.g101bc was discovered to contain a heap-use-after-free via the function expand_mmac_params at yasm/modules/preprocs/nasm/nasm-pp.c.

## References
- https://github.com/yasm/yasm/issues/221
- https://github.com/DaisyPo/fuzzing-vulncollect/tree/main/yasm/heap-use-after-free/nasm-pp.c:3878%20in%20expand_mmac_params
