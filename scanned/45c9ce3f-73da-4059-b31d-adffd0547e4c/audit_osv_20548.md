# [H] CVE-2021-3497

## Summary
Severity: High
Advisory: CVE-2021-3497
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-3497
Type: osv

## Details
GStreamer before 1.18.4 might access already-freed memory in error code paths when demuxing certain malformed Matroska files.

## References
- https://gstreamer.freedesktop.org/security/sa-2021-0002.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00027.html
- https://security.gentoo.org/glsa/202208-31
- https://www.debian.org/security/2021/dsa-4900
- https://bugzilla.redhat.com/show_bug.cgi?id=1945339
