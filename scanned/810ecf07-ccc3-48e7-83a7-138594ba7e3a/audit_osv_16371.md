# [H] CVE-2019-6245

## Summary
Severity: High
Advisory: CVE-2019-6245
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-01-13
Source: https://osv.dev/vulnerability/CVE-2019-6245
Type: osv

## Details
An issue was discovered in Anti-Grain Geometry (AGG) 2.4 as used in SVG++ (aka svgpp) 1.2.3. In the function agg::cell_aa::not_equal, dx is assigned to (x2 - x1). If dx >= dx_limit, which is (16384 << poly_subpixel_shift), this function will call itself recursively. There can be a situation where (x2 - x1) is always bigger than dx_limit during the recursion, leading to continual stack consumption.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00001.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00001.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00038.html
- https://github.com/svgpp/svgpp/issues/70
