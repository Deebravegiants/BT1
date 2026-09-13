# [H] CVE-2021-29457

## Summary
Severity: High
Advisory: CVE-2021-29457
Aliases: GHSA-v74w-h496-cgqm
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-29457
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. A heap buffer overflow was found in Exiv2 versions v0.27.3 and earlier. The heap overflow is triggered when Exiv2 is used to write metadata into a crafted image file. An attacker could potentially exploit the vulnerability to gain code execution, if they can trick the victim into running Exiv2 on a crafted image file. Note that this bug is only triggered when _writing_ the metadata, which is a less frequently used Exiv2 operation than _reading_ the metadata. For example, to trigger the bug in the Exiv2 command-line application, you need to add an extra command-line argument such as `insert`. The bug is fixed in version v0.27.4.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2XQT5F5IINTDYDAFGVGQZ7PMMLG7I5ZZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P2A5GMJEXQ5Q76JK6F6VKK5JYCLVFGKN/
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-v74w-h496-cgqm
- https://lists.debian.org/debian-lts-announce/2021/08/msg00028.html
- https://security.gentoo.org/glsa/202312-06
- https://www.debian.org/security/2021/dsa-4958
- https://github.com/Exiv2/exiv2/issues/1529
- https://github.com/Exiv2/exiv2/pull/1534
