# [H] CVE-2019-15538

## Summary
Severity: High
Advisory: CVE-2019-15538
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-25
Source: https://osv.dev/vulnerability/CVE-2019-15538
Type: osv

## Details
An issue was discovered in xfs_setattr_nonsize in fs/xfs/xfs_iops.c in the Linux kernel through 5.2.9. XFS partially wedges when a chgrp fails on account of being out of disk quota. xfs_setattr_nonsize is failing to unlock the ILOCK after the xfs_qm_vop_chown_reserve call fails. This is primarily a local DoS attack vector, but it might result as well in remote DoS if the XFS filesystem is exported for instance via NFS.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4JZ6AEUKFWBHQAROGMQARJ274PQP2QP/
- https://lore.kernel.org/linux-xfs/20190823035528.GH1037422%40magnolia/
- https://support.f5.com/csp/article/K32592426?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3RUDQJXRJQVGHCGR4YZWTQ3ECBI7TXH/
- https://lore.kernel.org/linux-xfs/20190823192433.GA8736%40eldamar.local
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://usn.ubuntu.com/4144-1/
- https://usn.ubuntu.com/4147-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1fb254aa983bf190cfd685d40c64a480a9bafaee
- https://github.com/torvalds/linux/commit/1fb254aa983bf190cfd685d40c64a480a9bafaee
