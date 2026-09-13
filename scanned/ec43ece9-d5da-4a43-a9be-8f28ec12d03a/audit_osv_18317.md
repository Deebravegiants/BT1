# [H] CVE-2020-26117

## Summary
Severity: High
Advisory: CVE-2020-26117
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2020-09-27
Source: https://osv.dev/vulnerability/CVE-2020-26117
Type: osv

## Details
In rfb/CSecurityTLS.cxx and rfb/CSecurityTLS.java in TigerVNC before 1.11.0, viewers mishandle TLS certificate exceptions. They store the certificates as authorities, meaning that the owner of a certificate could impersonate any server after a client had added an exception.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00024.html
- https://github.com/TigerVNC/tigervnc/releases/tag/v1.11.0
- https://lists.debian.org/debian-lts-announce/2020/10/msg00007.html
- https://bugzilla.opensuse.org/show_bug.cgi?id=1176733
- https://github.com/TigerVNC/tigervnc/commit/20dea801e747318525a5859fe4f37c52b05310cb
- https://github.com/TigerVNC/tigervnc/commit/7399eab79a4365434d26494fa1628ce1eb91562b
- https://github.com/TigerVNC/tigervnc/commit/b30f10c681ec87720cff85d490f67098568a9cba
- https://github.com/TigerVNC/tigervnc/commit/f029745f63ac7d22fb91639b2cb5b3ab56134d6e
