# [M] CVE-2016-2185

## Summary
Severity: Medium
Advisory: CVE-2016-2185
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-2185
Type: osv

## Details
The ati_remote2_probe function in drivers/input/misc/ati_remote2.c in the Linux kernel before 4.5.1 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) via a crafted endpoints value in a USB device descriptor.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.1
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securityfocus.com/bid/84341
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=950336ba3e4a1ffd2ca60d29f6ef386dd2c7351d
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://seclists.org/bugtraq/2016/Mar/116
- http://www.ubuntu.com/usn/USN-2997-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.ubuntu.com/usn/USN-2970-1
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-2968-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2971-2
- https://github.com/torvalds/linux/commit/950336ba3e4a1ffd2ca60d29f6ef386dd2c7351d
- http://www.ubuntu.com/usn/USN-2968-2
