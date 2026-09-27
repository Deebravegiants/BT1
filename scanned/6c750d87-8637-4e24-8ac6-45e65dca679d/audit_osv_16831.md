# [H] CVE-2019-9928

## Summary
Severity: High
Advisory: CVE-2019-9928
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-9928
Type: osv

## Details
GStreamer before 1.16.0 has a heap-based buffer overflow in the RTSP connection parser via a crafted response from a server, potentially allowing remote code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00082.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00049.html
- https://gstreamer.freedesktop.org/security/
- https://gstreamer.freedesktop.org/security/sa-2019-0001.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00030.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00031.html
- https://seclists.org/bugtraq/2019/Apr/39
- https://security.gentoo.org/glsa/202003-33
- https://usn.ubuntu.com/3958-1/
- https://www.debian.org/security/2019/dsa-4437
