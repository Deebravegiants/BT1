# [H] CVE-2021-29464

## Summary
Severity: High
Advisory: CVE-2021-29464
Aliases: GHSA-jgm9-5fw5-pw9p
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-29464
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. A heap buffer overflow was found in Exiv2 versions v0.27.3 and earlier. The heap overflow is triggered when Exiv2 is used to write metadata into a crafted image file. An attacker could potentially exploit the vulnerability to gain code execution, if they can trick the victim into running Exiv2 on a crafted image file. Note that this bug is only triggered when writing the metadata, which is a less frequently used Exiv2 operation than reading the metadata. For example, to trigger the bug in the Exiv2 command-line application, you need to add an extra command-line argument such as `insert`. The bug is fixed in version v0.27.4.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K3HKXR6JOVKMBE4HY4FDXNVZGNCQG6T3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NDMZTVQAZSMLPTDVDYLBHAAF7I5QXVYQ/
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-jgm9-5fw5-pw9p
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/commit/f9308839198aca5e68a65194f151a1de92398f54
