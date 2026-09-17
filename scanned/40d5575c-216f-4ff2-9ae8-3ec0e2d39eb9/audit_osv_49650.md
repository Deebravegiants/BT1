# [M] CVE-2019-15133

## Summary
Severity: Medium
Advisory: CVE-2019-15133
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-17
Source: https://osv.dev/vulnerability/CVE-2019-15133
Type: osv

## Details
In GIFLIB before 2019-02-16, a malformed GIF file triggers a divide-by-zero exception in the decoder function DGifSlurp in dgif_lib.c if the height field of the ImageSize data structure is equal to zero.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=13008
- https://lists.debian.org/debian-lts-announce/2022/12/msg00008.html
- https://usn.ubuntu.com/4107-1/
