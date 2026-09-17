# [M] JLSEC-2026-1309

## Summary
Severity: Medium
Advisory: JLSEC-2026-1309
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1309
Type: osv

## Affected
- Julia: `Exiv2_jll` — affected unspecified

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. An out-of-bounds read was found in Exiv2 versions v0.27.4 and earlier. The out-of-bounds read is triggered when Exiv2 is used to write metadata into a crafted image file. An attacker could potentially exploit the vulnerability to cause a denial of service by crashing Exiv2, if they can trick the victim into running Exiv2 on a crafted image file. Note that this bug is only triggered when writing the metadata, which is a less frequently used Exiv2 operation than reading the metadata. For example, to trigger the bug in the Exiv2 command-line application, you need to add an extra command-line argument such as insert. The bug is fixed in version v0.27.5.

## References
- https://github.com/Exiv2/exiv2/pull/1752
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-mxw9-qx4c-6m8v
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FMDT4PJB7P43WSOM3TRQIY3J33BAFVVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYGDELIFFJWKUU7SO3QATCIXCZJERGAC/
- https://security.gentoo.org/glsa/202312-06
