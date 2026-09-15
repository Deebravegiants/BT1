# [H] CVE-2020-13113

## Summary
Severity: High
Advisory: CVE-2020-13113
Aliases: A-196085005, ASB-A-196085005
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2020-05-21
Source: https://osv.dev/vulnerability/CVE-2020-13113
Type: osv

## Details
An issue was discovered in libexif before 0.6.22. Use of uninitialized memory in EXIF Makernote handling could lead to crashes and potential use-after-free conditions.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00025.html
- https://security.gentoo.org/glsa/202007-05
- https://usn.ubuntu.com/4396-1/
- https://github.com/libexif/libexif/commit/ec412aa4583ad71ecabb967d3c77162760169d1f
