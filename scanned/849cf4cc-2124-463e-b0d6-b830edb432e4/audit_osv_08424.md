# [M] CVE-2016-3136

## Summary
Severity: Medium
Advisory: CVE-2016-3136
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-3136
Type: osv

## Details
The mct_u232_msr_to_state function in drivers/usb/serial/mct_u232.c in the Linux kernel before 4.5.1 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) via a crafted USB device without two interrupt-in endpoint descriptors.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.1
- http://www.securityfocus.com/bid/84299
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4e9a0b05257f29cf4b75f3209243ed71614d062e
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00060.html
- http://www.openwall.com/lists/oss-security/2016/03/14/2
- https://www.exploit-db.com/exploits/39541/
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.ubuntu.com/usn/USN-2970-1
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2968-1
- http://www.ubuntu.com/usn/USN-2968-2
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2971-2
- http://www.ubuntu.com/usn/USN-2971-3
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-3000-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1317007
