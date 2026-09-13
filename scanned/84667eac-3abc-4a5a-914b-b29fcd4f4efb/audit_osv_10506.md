# [M] CVE-2017-16663

## Summary
Severity: Medium
Advisory: CVE-2017-16663
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-08
Source: https://osv.dev/vulnerability/CVE-2017-16663
Type: osv

## Details
In sam2p 0.49.4, there are integer overflows (with resultant heap-based buffer overflows) in input-bmp.ci in the function ReadImage, because "width * height" multiplications occur unsafely.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00031.html
- https://github.com/pts/sam2p/issues/16
