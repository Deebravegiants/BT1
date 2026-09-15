# [H] CVE-2018-17100

## Summary
Severity: High
Advisory: CVE-2018-17100
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-17100
Type: osv

## Details
An issue was discovered in LibTIFF 4.0.9. There is a int32 overflow in multiply_ms in tools/ppm2tiff.c, which can cause a denial of service (crash) or possibly have unspecified other impact via a crafted image file.

## References
- https://usn.ubuntu.com/3906-2/
- https://access.redhat.com/errata/RHSA-2019:2053
- https://lists.debian.org/debian-lts-announce/2018/10/msg00019.html
- https://usn.ubuntu.com/3864-1/
- https://www.debian.org/security/2020/dsa-4670
- http://bugzilla.maptools.org/show_bug.cgi?id=2810
- https://gitlab.com/libtiff/libtiff/merge_requests/33/diffs?commit_id=6da1fb3f64d43be37e640efbec60400d1f1ac39e
