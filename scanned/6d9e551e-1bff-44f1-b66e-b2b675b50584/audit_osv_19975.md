# [M] CVE-2021-28855

## Summary
Severity: Medium
Advisory: CVE-2021-28855
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2021-28855
Type: osv

## Details
In Deark before 1.5.8, a specially crafted input file can cause a NULL pointer dereference in the dbuf_write function (src/deark-dbuf.c).

## References
- https://github.com/fuzzing2026/CVE-PoCs/tree/main/deark-CVE-2021-28855
- https://fatihhcelik.github.io/posts/NULL-Pointer-Dereference-Deark/
- https://github.com/jsummers/deark/commit/287f5ac31dfdc074669182f51ece637706070eeb
