# [M] JLSEC-2026-1310

## Summary
Severity: Medium
Advisory: JLSEC-2026-1310
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1310
Type: osv

## Affected
- Julia: `Exiv2_jll` — affected unspecified

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. An out-of-bounds read was found in Exiv2 versions v0.27.4 and earlier. The out-of-bounds read is triggered when Exiv2 is used to read the metadata of a crafted image file. An attacker could potentially exploit the vulnerability to cause a denial of service, if they can trick the victim into running Exiv2 on a crafted image file. The bug is fixed in version v0.27.5.

## References
- https://github.com/Exiv2/exiv2/pull/1769
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-v5g7-46xf-h728
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FMDT4PJB7P43WSOM3TRQIY3J33BAFVVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYGDELIFFJWKUU7SO3QATCIXCZJERGAC/
- https://security.gentoo.org/glsa/202312-06
