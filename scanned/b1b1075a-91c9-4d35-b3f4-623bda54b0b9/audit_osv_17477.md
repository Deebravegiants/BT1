# [M] CVE-2020-15304

## Summary
Severity: Medium
Advisory: CVE-2020-15304
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-26
Source: https://osv.dev/vulnerability/CVE-2020-15304
Type: osv

## Details
An issue was discovered in OpenEXR before 2.5.2. An invalid tiled input file could cause invalid memory access in TiledInputFile::TiledInputFile() in IlmImf/ImfTiledInputFile.cpp, as demonstrated by a NULL pointer dereference.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LKDRVXORM2VLNHRLFKS3JHRABSHZ5W5M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SHYAKRAUEMYVCV7U5WLDRE2YFGSV5PIT/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00048.html
- https://github.com/AcademySoftwareFoundation/openexr/blob/master/CHANGES.md
- https://github.com/AcademySoftwareFoundation/openexr/blob/master/SECURITY.md
- https://github.com/AcademySoftwareFoundation/openexr/pull/727
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v2.5.2
- https://security.gentoo.org/glsa/202107-27
