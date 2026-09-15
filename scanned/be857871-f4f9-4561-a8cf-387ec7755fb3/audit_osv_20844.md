# [M] CVE-2021-37620

## Summary
Severity: Medium
Advisory: CVE-2021-37620
Aliases: GHSA-v5g7-46xf-h728
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-09
Source: https://osv.dev/vulnerability/CVE-2021-37620
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. An out-of-bounds read was found in Exiv2 versions v0.27.4 and earlier. The out-of-bounds read is triggered when Exiv2 is used to read the metadata of a crafted image file. An attacker could potentially exploit the vulnerability to cause a denial of service, if they can trick the victim into running Exiv2 on a crafted image file. The bug is fixed in version v0.27.5.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FMDT4PJB7P43WSOM3TRQIY3J33BAFVVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYGDELIFFJWKUU7SO3QATCIXCZJERGAC/
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-v5g7-46xf-h728
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/pull/1769
