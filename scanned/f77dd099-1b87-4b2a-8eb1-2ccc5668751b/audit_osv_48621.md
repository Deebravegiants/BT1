# [H] CVE-2018-10111

## Summary
Severity: High
Advisory: CVE-2018-10111
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-10111
Type: osv

## Details
An issue was discovered in GEGL through 0.3.32. The render_rectangle function in process/gegl-processor.c has unbounded memory allocation, leading to a denial of service (application crash) upon allocation failure.

## References
- https://github.com/xiaoqx/pocs/tree/master/gegl
