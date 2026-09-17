# [M] CVE-2019-20811

## Summary
Severity: Medium
Advisory: CVE-2019-20811
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2019-20811
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.6. In rx_queue_add_kobject() and netdev_queue_add_kobject() in net/core/net-sysfs.c, a reference count is mishandled, aka CID-a3e23f719f5c.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.6
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://usn.ubuntu.com/4527-1/
- https://www.debian.org/security/2020/dsa-4698
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a3e23f719f5c4a38ffb3d30c8d7632a4ed8ccd9e
