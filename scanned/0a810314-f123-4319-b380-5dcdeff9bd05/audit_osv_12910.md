# [M] CVE-2018-16323

## Summary
Severity: Medium
Advisory: CVE-2018-16323
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-09-01
Source: https://osv.dev/vulnerability/CVE-2018-16323
Type: osv

## Details
ReadXBMImage in coders/xbm.c in ImageMagick before 7.0.8-9 leaves data uninitialized when processing an XBM file that has a negative pixel value. If the affected code is used as a library loaded into a process that includes sensitive information, that information sometimes can be leaked via the image data.

## References
- https://usn.ubuntu.com/3785-1/
- https://usn.ubuntu.com/4034-1/
- https://github.com/ImageMagick/ImageMagick/commit/216d117f05bff87b9dc4db55a1b1fadb38bcb786
- https://www.exploit-db.com/exploits/45890/
