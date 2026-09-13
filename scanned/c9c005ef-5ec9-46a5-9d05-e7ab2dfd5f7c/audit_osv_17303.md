# [H] CVE-2020-14399

## Summary
Severity: High
Advisory: CVE-2020-14399
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2020-14399
Type: osv

## Details
An issue was discovered in LibVNCServer before 0.9.13. Byte-aligned data is accessed through uint32_t pointers in libvncclient/rfbproto.c. NOTE: there is reportedly "no trust boundary crossed.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00066.html
- https://github.com/LibVNC/libvncserver/compare/LibVNCServer-0.9.12...LibVNCServer-0.9.13
- https://lists.debian.org/debian-lts-announce/2020/06/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00045.html
- https://usn.ubuntu.com/4434-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1860354
- https://github.com/LibVNC/libvncserver/commit/23e5cbe6b090d7f22982aee909a6a618174d3c2d
