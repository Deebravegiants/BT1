# [H] CVE-2017-16612

## Summary
Severity: High
Advisory: CVE-2017-16612
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/CVE-2017-16612
Type: osv

## Details
libXcursor before 1.1.15 has various integer overflows that could lead to heap buffer overflows when processing malicious cursors, e.g., with programs like GIMP. It is also possible that an attack vector exists against the related code in cursor/xcursor.c in Wayland through 1.14.0.

## References
- https://cgit.freedesktop.org/wayland/wayland/commit/?id=5d201df72f3d4f4cb8b8f75f980169b03507da38
- https://lists.debian.org/debian-lts-announce/2017/12/msg00002.html
- https://lists.freedesktop.org/archives/wayland-devel/2017-November/035979.html
- https://usn.ubuntu.com/3622-1/
- http://www.openwall.com/lists/oss-security/2017/11/28/6
- http://www.ubuntu.com/usn/USN-3501-1
- https://marc.info/?l=freedesktop-xorg-announce&m=151188036018262&w=2
- https://security.gentoo.org/glsa/201801-04
- https://www.debian.org/security/2017/dsa-4059
- https://bugzilla.suse.com/show_bug.cgi?id=1065386
- http://security.cucumberlinux.com/security/details.php?id=156
- https://cgit.freedesktop.org/xorg/lib/libXcursor/commit/?id=4794b5dd34688158fb51a2943032569d3780c4b8
