# [M] CVE-2016-6480

## Summary
Severity: Medium
Advisory: CVE-2016-6480
CVSS: 5.1 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6480
Type: osv

## Details
Race condition in the ioctl_send_fib function in drivers/scsi/aacraid/commctrl.c in the Linux kernel through 4.7 allows local users to cause a denial of service (out-of-bounds access or system crash) by changing a certain size value, aka a "double fetch" vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00001.html
- http://www.securityfocus.com/bid/92214
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://rhn.redhat.com/errata/RHSA-2017-0817.html
- http://www.securityfocus.com/archive/1/539074/30/0/threaded
- https://bugzilla.redhat.com/show_bug.cgi?id=1362466
