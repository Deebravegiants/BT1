# [M] CVE-2016-3951

## Summary
Severity: Medium
Advisory: CVE-2016-3951
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-3951
Type: osv

## Details
Double free vulnerability in drivers/net/usb/cdc_ncm.c in the Linux kernel before 4.5 allows physically proximate attackers to cause a denial of service (system crash) or possibly have unspecified other impact by inserting a USB device with an invalid USB descriptor.

## References
- http://www.openwall.com/lists/oss-security/2016/04/06/4
- https://www.spinics.net/lists/netdev/msg367669.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00060.html
- http://www.securityfocus.com/bid/91028
- http://www.securitytracker.com/id/1036763
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1666984c8625b3db19a9abc298931d35ab7bc64b
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2998-1
- http://www.ubuntu.com/usn/USN-3003-1
- http://www.ubuntu.com/usn/USN-3004-1
- http://www.ubuntu.com/usn/USN-3021-1
- https://github.com/torvalds/linux/commit/1666984c8625b3db19a9abc298931d35ab7bc64b
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4d06dd537f95683aba3651098ae288b7cbff8274
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://www.ubuntu.com/usn/USN-2989-1
- http://www.ubuntu.com/usn/USN-3021-2
- https://github.com/torvalds/linux/commit/4d06dd537f95683aba3651098ae288b7cbff8274
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.ubuntu.com/usn/USN-3000-1
