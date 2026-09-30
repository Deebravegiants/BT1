# [M] In LibTIFF, there is a memory malloc failure in `tif_pixarlog.c`

## Summary
Severity: Medium
Advisory: JLSEC-2025-256
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-256
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.3.0+0

## Details
In LibTIFF, there is a memory malloc failure in `tif_pixarlog.c`. A crafted TIFF document can lead to an abort, resulting in a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1932037
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMHBYFMX3D5VGR6Y3RXTTH3Q4NF4E6IG/
- https://security.gentoo.org/glsa/202104-06
- https://security.netapp.com/advisory/ntap-20210521-0009/
