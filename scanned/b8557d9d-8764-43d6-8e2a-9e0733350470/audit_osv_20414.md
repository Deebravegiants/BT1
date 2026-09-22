# [M] CVE-2021-33467

## Summary
Severity: Medium
Advisory: CVE-2021-33467
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-07-26
Source: https://osv.dev/vulnerability/CVE-2021-33467
Type: osv

## Details
An issue was discovered in yasm version 1.3.0. There is a use-after-free in pp_getline() in modules/preprocs/nasm/nasm-pp.c.

## References
- https://gist.github.com/Clingto/bb632c0c463f4b2c97e4f65f751c5e6d
- https://github.com/yasm/yasm/issues/163
