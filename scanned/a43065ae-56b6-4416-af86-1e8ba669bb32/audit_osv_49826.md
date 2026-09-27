# [M] CVE-2019-19529

## Summary
Severity: Medium
Advisory: CVE-2019-19529
CVSS: 6.3 (CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19529
Type: osv

## Details
In the Linux kernel before 5.3.11, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/net/can/usb/mcba_usb.c driver, aka CID-4d6636498c41.

## References
- https://usn.ubuntu.com/4227-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4227-2/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11
- https://usn.ubuntu.com/4225-2/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4d6636498c41891d0482a914dd570343a838ad79
