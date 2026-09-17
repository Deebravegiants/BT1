# [H] CVE-2021-41737

## Summary
Severity: High
Advisory: CVE-2021-41737
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2021-41737
Type: osv

## Details
In Faust 2.23.1, an input file with the lines "// r visualisation tCst" and "//process = +: L: abM-^Q;" and "process = route(3333333333333333333,2,1,2,3,1) : *;" leads to stack consumption.

## References
- https://github.com/grame-cncm/faust/tree/e682dbeeb7cc0ec9a1fcb6872f53433e454aa233
- https://github.com/grame-cncm/faust/issues/653
