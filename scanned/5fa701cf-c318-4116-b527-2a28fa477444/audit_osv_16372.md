# [C] CVE-2019-6246

## Summary
Severity: Critical
Advisory: CVE-2019-6246
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-13
Source: https://osv.dev/vulnerability/CVE-2019-6246
Type: osv

## Details
An issue was discovered in SVG++ (aka svgpp) 1.2.3. After calling the gil::get_color function in Generic Image Library in Boost, the return code is used as an address, leading to an Access Violation because of an out-of-bounds read.

## References
- https://github.com/svgpp/svgpp/issues/70
