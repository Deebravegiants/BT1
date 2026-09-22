# [H] CVE-2019-20421

## Summary
Severity: High
Advisory: CVE-2019-20421
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/CVE-2019-20421
Type: osv

## Details
In Jp2Image::readMetadata() in jp2image.cpp in Exiv2 0.27.2, an input file can result in an infinite loop and hang, with high CPU consumption. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00028.html
- https://usn.ubuntu.com/4270-1/
- https://www.debian.org/security/2021/dsa-4958
- https://github.com/Exiv2/exiv2/commit/a82098f4f90cd86297131b5663c3dec6a34470e8
- https://github.com/Exiv2/exiv2/issues/1011
