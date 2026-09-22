# [H] A heap-based buffer overflow flaw was found in libtiff in the handling of TIFF images in libtiff's...

## Summary
Severity: High
Advisory: JLSEC-2025-258
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-258
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.3.0+0

## Details
A heap-based buffer overflow flaw was found in libtiff in the handling of TIFF images in libtiff's TIFF2PDF tool. A specially crafted TIFF file can lead to arbitrary code execution. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1932044
- https://gitlab.com/libtiff/libtiff/-/merge_requests/159
- https://gitlab.com/rzkn/libtiff/-/commit/7be2e452ddcf6d7abca88f41d3761e6edab72b22
- https://lists.debian.org/debian-lts-announce/2021/06/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMHBYFMX3D5VGR6Y3RXTTH3Q4NF4E6IG/
- https://security.gentoo.org/glsa/202104-06
- https://security.netapp.com/advisory/ntap-20210521-0009/
- https://www.debian.org/security/2021/dsa-4869
