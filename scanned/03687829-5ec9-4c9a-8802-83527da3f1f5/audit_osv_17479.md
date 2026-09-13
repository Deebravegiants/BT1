# [M] CVE-2020-15306

## Summary
Severity: Medium
Advisory: CVE-2020-15306
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-26
Source: https://osv.dev/vulnerability/CVE-2020-15306
Type: osv

## Details
An issue was discovered in OpenEXR before v2.5.2. Invalid chunkCount attributes could cause a heap buffer overflow in getChunkOffsetTableSize() in IlmImf/ImfMisc.cpp.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LKDRVXORM2VLNHRLFKS3JHRABSHZ5W5M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SHYAKRAUEMYVCV7U5WLDRE2YFGSV5PIT/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00048.html
- https://github.com/AcademySoftwareFoundation/openexr/blob/master/CHANGES.md
- https://github.com/AcademySoftwareFoundation/openexr/blob/master/SECURITY.md
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v2.5.2
- https://lists.debian.org/debian-lts-announce/2020/08/msg00056.html
- https://security.gentoo.org/glsa/202107-27
- https://usn.ubuntu.com/4418-1/
- https://www.debian.org/security/2020/dsa-4755
- https://github.com/AcademySoftwareFoundation/openexr/pull/738
