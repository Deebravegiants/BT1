# [M] CVE-2019-3819

## Summary
Severity: Medium
Advisory: CVE-2019-3819
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-25
Source: https://osv.dev/vulnerability/CVE-2019-3819
Type: osv

## Details
A flaw was found in the Linux kernel in the function hid_debug_events_read() in drivers/hid/hid-debug.c file which may enter an infinite loop with certain parameters passed from a userspace. A local privileged user ("root") can cause a system lock up and a denial of service. Versions from v4.18 and newer are vulnerable.

## References
- https://usn.ubuntu.com/3932-1/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://usn.ubuntu.com/3932-2/
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00052.html
- http://www.securityfocus.com/bid/106730
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3819
