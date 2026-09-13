# [M] CVE-2020-12652

## Summary
Severity: Medium
Advisory: CVE-2020-12652
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-12652
Type: osv

## Details
The __mptctl_ioctl function in drivers/message/fusion/mptctl.c in the Linux kernel before 5.4.14 allows local users to hold an incorrect lock during the ioctl operation and trigger a race condition, i.e., a "double fetch" vulnerability, aka CID-28d76df18f0a. NOTE: the vendor states "The security impact of this bug is not as bad as it could have been because these operations are all privileged and root already has enormous destructive power."

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://www.debian.org/security/2020/dsa-4698
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.14
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=28d76df18f0ad5bcf5fa48510b225f0ed262a99b
- https://github.com/torvalds/linux/commit/28d76df18f0ad5bcf5fa48510b225f0ed262a99b
