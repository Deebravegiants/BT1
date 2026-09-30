# [M] CVE-2016-6828

## Summary
Severity: Medium
Advisory: CVE-2016-6828
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-6828
Type: osv

## Details
The tcp_check_send_head function in include/net/tcp.h in the Linux kernel before 4.7.5 does not properly maintain certain SACK state after a failed data copy, which allows local users to cause a denial of service (tcp_xmit_retransmit_queue use-after-free and system crash) via a crafted SACK option.

## References
- http://www.securityfocus.com/bid/92452
- https://marcograss.github.io/security/linux/2016/08/18/cve-2016-6828-linux-kernel-tcp-uaf.html
- https://source.android.com/security/bulletin/2016-11-01.html
- http://rhn.redhat.com/errata/RHSA-2017-0091.html
- http://rhn.redhat.com/errata/RHSA-2017-0113.html
- http://rhn.redhat.com/errata/RHSA-2017-0036.html
- http://rhn.redhat.com/errata/RHSA-2017-0086.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.5
- https://bugzilla.redhat.com/show_bug.cgi?id=1367091
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=bb1fceca22492109be12640d49f5ea5a544c6bb4
- https://github.com/torvalds/linux/commit/bb1fceca22492109be12640d49f5ea5a544c6bb4
- http://www.openwall.com/lists/oss-security/2016/08/15/1
