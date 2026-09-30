# [H] An integer overflow flaw was found in libtiff that exists in the `tif_getimage.c` file

## Summary
Severity: High
Advisory: JLSEC-2025-257
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-257
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.3.0+0

## Details
An integer overflow flaw was found in libtiff that exists in the `tif_getimage.c` file. This flaw allows an attacker to inject and execute arbitrary code when a user opens a crafted TIFF file. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1932040
- https://gitlab.com/libtiff/libtiff/-/commit/c8d613ef497058fe653c467fc84c70a62a4a71b2
- https://gitlab.com/libtiff/libtiff/-/merge_requests/160
- https://lists.debian.org/debian-lts-announce/2021/06/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BMHBYFMX3D5VGR6Y3RXTTH3Q4NF4E6IG/
- https://security.gentoo.org/glsa/202104-06
- https://security.netapp.com/advisory/ntap-20210521-0009/
- https://www.debian.org/security/2021/dsa-4869
