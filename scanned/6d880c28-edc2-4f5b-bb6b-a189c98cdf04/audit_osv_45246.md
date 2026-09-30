# [M] A flaw was found in libtiff

## Summary
Severity: Medium
Advisory: JLSEC-2025-255
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-255
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.3.0+0

## Details
A flaw was found in libtiff. Due to a memory allocation failure in `tif_read.c`, a crafted TIFF file can lead to an abort, resulting in denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1932034
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMHBYFMX3D5VGR6Y3RXTTH3Q4NF4E6IG/
- https://security.gentoo.org/glsa/202104-06
- https://security.netapp.com/advisory/ntap-20210521-0009/
