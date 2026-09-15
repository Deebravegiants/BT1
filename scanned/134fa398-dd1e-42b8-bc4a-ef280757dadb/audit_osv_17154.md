# [H] CVE-2020-13114

## Summary
Severity: High
Advisory: CVE-2020-13114
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-13114
Type: osv

## Details
An issue was discovered in libexif before 0.6.22. An unrestricted size in handling Canon EXIF MakerNote data could lead to consumption of large amounts of compute time for decoding EXIF data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00025.html
- https://security.gentoo.org/glsa/202007-05
- https://usn.ubuntu.com/4396-1/
- https://github.com/libexif/libexif/commit/e6a38a1a23ba94d139b1fa2cd4519fdcfe3c9bab
