# [M] CVE-2020-19144

## Summary
Severity: Medium
Advisory: CVE-2020-19144
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-09
Source: https://osv.dev/vulnerability/CVE-2020-19144
Type: osv

## Details
Buffer Overflow in LibTiff v4.0.10 allows attackers to cause a denial of service via the 'in _TIFFmemcpy' funtion in the component 'tif_unix.c'.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00004.html
- https://security.netapp.com/advisory/ntap-20211004-0005/
- http://bugzilla.maptools.org/show_bug.cgi?id=2852
- https://gitlab.com/libtiff/libtiff/-/issues/159
