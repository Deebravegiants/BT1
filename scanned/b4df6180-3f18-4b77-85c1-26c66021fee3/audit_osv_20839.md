# [M] CVE-2021-37615

## Summary
Severity: Medium
Advisory: CVE-2021-37615
Aliases: GHSA-h9x9-4f77-336w
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-09
Source: https://osv.dev/vulnerability/CVE-2021-37615
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. A null pointer dereference was found in Exiv2 versions v0.27.4 and earlier. The null pointer dereference is triggered when Exiv2 is used to print the metadata of a crafted image file. An attacker could potentially exploit the vulnerability to cause a denial of service, if they can trick the victim into running Exiv2 on a crafted image file. Note that this bug is only triggered when printing the interpreted (translated) data, which is a less frequently used Exiv2 operation that requires an extra command line option (`-p t` or `-P t`). The bug is fixed in version v0.27.5.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FMDT4PJB7P43WSOM3TRQIY3J33BAFVVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYGDELIFFJWKUU7SO3QATCIXCZJERGAC/
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-h9x9-4f77-336w
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/pull/1758
