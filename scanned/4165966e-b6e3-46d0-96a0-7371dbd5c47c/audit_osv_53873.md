# [M] CVE-2023-29580

## Summary
Severity: Medium
Advisory: CVE-2023-29580
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-12
Source: https://osv.dev/vulnerability/CVE-2023-29580
Type: osv

## Details
yasm 1.3.0.55.g101bc was discovered to contain a segmentation violation via the component yasm_expr_create at /libyasm/expr.c.

## References
- https://github.com/yasm/yasm/issues/215
- https://github.com/z1r00/fuzz_vuln/blob/main/yasm/segv/yasm_expr_create/readmd.md
