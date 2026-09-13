# [M] CVE-2021-29470

## Summary
Severity: Medium
Advisory: CVE-2021-29470
Aliases: GHSA-8949-hhfh-j7rj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-23
Source: https://osv.dev/vulnerability/CVE-2021-29470
Type: osv

## Details
Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. An out-of-bounds read was found in Exiv2 versions v0.27.3 and earlier. The out-of-bounds read is triggered when Exiv2 is used to write metadata into a crafted image file. An attacker could potentially exploit the vulnerability to cause a denial of service by crashing Exiv2, if they can trick the victim into running Exiv2 on a crafted image file. Note that this bug is only triggered when writing the metadata, which is a less frequently used Exiv2 operation than reading the metadata. For example, to trigger the bug in the Exiv2 command-line application, you need to add an extra command-line argument such as insert. The bug is fixed in version v0.27.4.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2XQT5F5IINTDYDAFGVGQZ7PMMLG7I5ZZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWZLDECIXXW3CCZ3RS4A3NG5X5VE4WZM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBKWLTXM7IKZ4PVGKLUQVAVFAYGGF7QR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P2A5GMJEXQ5Q76JK6F6VKK5JYCLVFGKN/
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/pull/1581
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-8949-hhfh-j7rj
