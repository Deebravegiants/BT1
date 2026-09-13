# [M] CVE-2020-11765

## Summary
Severity: Medium
Advisory: CVE-2020-11765
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/CVE-2020-11765
Type: osv

## Details
An issue was discovered in OpenEXR before 2.4.1. There is an off-by-one error in use of the ImfXdr.h read function by DwaCompressor::Classifier::Classifier, leading to an out-of-bounds read.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F4KFGDQG5PVYAU7TS5MZ7XCS6EMPVII3/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00051.html
- https://github.com/AcademySoftwareFoundation/openexr/blob/master/CHANGES.md#version-241-february-11-2020
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v2.4.1
- https://lists.debian.org/debian-lts-announce/2020/08/msg00056.html
- https://security.gentoo.org/glsa/202107-27
- https://support.apple.com/kb/HT211288
- https://support.apple.com/kb/HT211289
- https://support.apple.com/kb/HT211290
- https://support.apple.com/kb/HT211291
- https://support.apple.com/kb/HT211293
- https://support.apple.com/kb/HT211294
- https://support.apple.com/kb/HT211295
- https://usn.ubuntu.com/4339-1/
- https://www.debian.org/security/2020/dsa-4755
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1987
