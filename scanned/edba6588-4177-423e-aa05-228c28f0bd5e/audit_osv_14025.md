# [M] CVE-2018-6405

## Summary
Severity: Medium
Advisory: CVE-2018-6405
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-30
Source: https://osv.dev/vulnerability/CVE-2018-6405
Type: osv

## Details
In the ReadDCMImage function in coders/dcm.c in ImageMagick before 7.0.7-23, each redmap, greenmap, and bluemap variable can be overwritten by a new pointer. The previous pointer is lost, which leads to a memory leak. This allows remote attackers to cause a denial of service.

## References
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/964
