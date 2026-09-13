# [M] CVE-2020-10751

## Summary
Severity: Medium
Advisory: CVE-2020-10751
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2020-05-26
Source: https://osv.dev/vulnerability/CVE-2020-10751
Type: osv

## Details
A flaw was found in the Linux kernels SELinux LSM hook implementation before version 5.7, where it incorrectly assumed that an skb would only contain a single netlink message. The hook would incorrectly only validate the first netlink message in the skb and allow or deny the rest of the messages within the skb with the granted permission without further processing.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00008.html
- https://usn.ubuntu.com/4412-1/
- https://www.oracle.com/security-alerts/cpuApr2021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://usn.ubuntu.com/4389-1/
- https://usn.ubuntu.com/4391-1/
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://lore.kernel.org/selinux/CACT4Y+b8HiV6KFuAPysZD=5hmyO4QisgxCKi4DHU3CfMPSP=yg%40mail.gmail.com/
- https://usn.ubuntu.com/4390-1/
- https://usn.ubuntu.com/4413-1/
- https://www.debian.org/security/2020/dsa-4699
- https://www.debian.org/security/2020/dsa-4698
- https://www.openwall.com/lists/oss-security/2020/04/30/5
- http://www.openwall.com/lists/oss-security/2020/05/27/3
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fb73974172ffaaf57a7c42f35424d9aece1a5af6
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10751
