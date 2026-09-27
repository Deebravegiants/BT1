# [H] CVE-2021-27364

## Summary
Severity: High
Advisory: CVE-2021-27364
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-03-07
Source: https://osv.dev/vulnerability/CVE-2021-27364
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.3. drivers/scsi/scsi_transport_iscsi.c is adversely affected by the ability of an unprivileged user to craft Netlink messages.

## References
- https://security.netapp.com/advisory/ntap-20210409-0001/
- http://packetstormsecurity.com/files/162117/Kernel-Live-Patch-Security-Notice-LSN-0075-1.html
- https://www.openwall.com/lists/oss-security/2021/03/06/1
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://bugzilla.suse.com/show_bug.cgi?id=1182717
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=688e8128b7a92df982709a4137ea4588d16f24aa
- https://blog.grimm-co.com/2021/03/new-old-bugs-in-linux-kernel.html
