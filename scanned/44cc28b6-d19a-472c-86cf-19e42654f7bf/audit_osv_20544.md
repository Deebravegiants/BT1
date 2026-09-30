# [M] CVE-2021-3482

## Summary
Severity: Medium
Advisory: CVE-2021-3482
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-3482
Type: osv

## Details
A flaw was found in Exiv2 in versions before and including 0.27.4-RC1. Improper input validation of the rawData.size property in Jp2Image::readMetadata() in jp2image.cpp can lead to a heap-based buffer overflow via a crafted JPG image containing malicious EXIF data.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2XQT5F5IINTDYDAFGVGQZ7PMMLG7I5ZZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P2A5GMJEXQ5Q76JK6F6VKK5JYCLVFGKN/
- https://lists.debian.org/debian-lts-announce/2021/08/msg00028.html
- https://www.debian.org/security/2021/dsa-4958
- https://bugzilla.redhat.com/show_bug.cgi?id=1946314
