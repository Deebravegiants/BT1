# [C] CVE-2020-13112

## Summary
Severity: Critical
Advisory: CVE-2020-13112
Aliases: A-194342672, ASB-A-194342672
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-13112
Type: osv

## Details
An issue was discovered in libexif before 0.6.22. Several buffer over-reads in EXIF MakerNote handling could lead to information disclosure and crashes. This is different from CVE-2020-0093.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00025.html
- https://security.gentoo.org/glsa/202007-05
- https://usn.ubuntu.com/4396-1/
- https://github.com/libexif/libexif/commit/435e21f05001fb03f9f186fa7cbc69454afd00d1
