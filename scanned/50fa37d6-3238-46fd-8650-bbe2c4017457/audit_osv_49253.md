# [H] CVE-2018-7587

## Summary
Severity: High
Advisory: CVE-2018-7587
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2018-7587
Type: osv

## Details
An issue was discovered in CImg v.220. DoS occurs when loading a crafted bmp image that triggers an allocation failure in load_bmp in CImg.h.

## References
- https://usn.ubuntu.com/4039-1/
- https://github.com/xiaoqx/pocs/tree/master/cimg
