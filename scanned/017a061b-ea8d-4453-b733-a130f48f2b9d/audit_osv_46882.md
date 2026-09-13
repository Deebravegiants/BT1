# [M] CVE-2015-7566

## Summary
Severity: Medium
Advisory: CVE-2015-7566
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2015-7566
Type: osv

## Details
The clie_5_attach function in drivers/usb/serial/visor.c in the Linux kernel through 4.4.1 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) or possibly have unspecified other impact by inserting a USB device that lacks a bulk-out endpoint.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cb3232138e37129e88240a98a1d2aba2187ff57c
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.debian.org/security/2016/dsa-3448
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2929-1
- http://www.ubuntu.com/usn/USN-2929-2
- http://www.ubuntu.com/usn/USN-2930-1
- http://www.ubuntu.com/usn/USN-2930-2
- http://www.ubuntu.com/usn/USN-2930-3
- http://www.ubuntu.com/usn/USN-2932-1
- http://www.ubuntu.com/usn/USN-2948-1
- http://www.ubuntu.com/usn/USN-2948-2
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2967-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1283371
- https://bugzilla.redhat.com/show_bug.cgi?id=1296466
- https://security-tracker.debian.org/tracker/CVE-2015-7566
- https://github.com/torvalds/linux/commit/cb3232138e37129e88240a98a1d2aba2187ff57c
