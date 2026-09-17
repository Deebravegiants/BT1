# [M] CVE-2016-5104

## Summary
Severity: Medium
Advisory: CVE-2016-5104
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-5104
Type: osv

## Details
The socket_create function in common/socket.c in libimobiledevice and libusbmuxd allows remote attackers to bypass intended access restrictions and communicate with services on iOS devices by connecting to an IPv4 TCP socket.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00042.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00029.html
- http://www.openwall.com/lists/oss-security/2016/05/26/1
- http://www.openwall.com/lists/oss-security/2016/05/26/6
- https://lists.debian.org/debian-lts-announce/2020/02/msg00027.html
- https://lists.debian.org/debian-lts-announce/2020/02/msg00028.html
- http://www.ubuntu.com/usn/USN-3026-1
- http://www.ubuntu.com/usn/USN-3026-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1339988
- https://github.com/libimobiledevice/libimobiledevice/commit/df1f5c4d70d0c19ad40072f5246ca457e7f9849e
- https://github.com/libimobiledevice/libusbmuxd/commit/4397b3376dc4e4cb1c991d0aed61ce6482614196
