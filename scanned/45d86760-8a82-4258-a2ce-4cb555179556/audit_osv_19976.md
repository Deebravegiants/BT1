# [M] CVE-2021-28856

## Summary
Severity: Medium
Advisory: CVE-2021-28856
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2021-28856
Type: osv

## Details
In Deark before v1.5.8, a specially crafted input file can cause a division by zero in (src/fmtutil.c) because of the value of pixelsize.

## References
- https://github.com/fuzzing2026/CVE-PoCs/tree/main/deark-CVE-2021-28856
- https://fatihhcelik.github.io/posts/Division-By-Zero-Deark/
- https://github.com/jsummers/deark/commit/62acb7753b0e3c0d3ab3c15057b0a65222313334
