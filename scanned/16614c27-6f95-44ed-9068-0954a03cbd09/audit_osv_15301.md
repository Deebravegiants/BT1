# [M] CVE-2019-15139

## Summary
Severity: Medium
Advisory: CVE-2019-15139
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-18
Source: https://osv.dev/vulnerability/CVE-2019-15139
Type: osv

## Details
The XWD image (X Window System window dumping file) parsing component in ImageMagick 7.0.8-41 Q16 allows attackers to cause a denial-of-service (application crash resulting from an out-of-bounds Read) in ReadXWDImage in coders/xwd.c by crafting a corrupted XWD image file, a different vulnerability than CVE-2019-11472.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3IYH7QSNXXOIDFTYLY455ANZ3JWQ7FCS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FS76VNCFL3FVRMGXQEMHBOKA7EE46BTS/
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/commit/c78993d138bf480ab4652b5a48379d4ff75ba5f7
- https://github.com/ImageMagick/ImageMagick/issues/1553
