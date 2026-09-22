# [M] CVE-2015-7515

## Summary
Severity: Medium
Advisory: CVE-2015-7515
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2015-7515
Type: osv

## Details
The aiptek_probe function in drivers/input/tablet/aiptek.c in the Linux kernel before 4.4 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) via a crafted USB device that lacks endpoints.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8e20cf2bce122ce9262d6034ee5d5b76fbb92f96
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.securityfocus.com/bid/84288
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2967-2
- http://www.ubuntu.com/usn/USN-2968-1
- http://www.ubuntu.com/usn/USN-2968-2
- http://www.ubuntu.com/usn/USN-2969-1
- http://www.ubuntu.com/usn/USN-2970-1
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2971-2
- http://www.ubuntu.com/usn/USN-2971-3
- https://github.com/torvalds/linux/commit/8e20cf2bce122ce9262d6034ee5d5b76fbb92f96
- https://security-tracker.debian.org/tracker/CVE-2015-7515
- https://www.exploit-db.com/exploits/39544/
- https://bugzilla.redhat.com/show_bug.cgi?id=1285326
