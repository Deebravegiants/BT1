# [M] CVE-2016-3139

## Summary
Severity: Medium
Advisory: CVE-2016-3139
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-3139
Type: osv

## Details
The wacom_probe function in drivers/input/tablet/wacom_sys.c in the Linux kernel before 3.17 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) via a crafted endpoints value in a USB device descriptor.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=471d17148c8b4174ac5f5283a73316d12c4379bc
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- https://security-tracker.debian.org/tracker/CVE-2016-3139
- https://www.exploit-db.com/exploits/39538/
- https://bugzilla.redhat.com/show_bug.cgi?id=1283377
- https://bugzilla.redhat.com/show_bug.cgi?id=1283375
- https://bugzilla.redhat.com/show_bug.cgi?id=1316993
- https://github.com/torvalds/linux/commit/471d17148c8b4174ac5f5283a73316d12c4379bc
