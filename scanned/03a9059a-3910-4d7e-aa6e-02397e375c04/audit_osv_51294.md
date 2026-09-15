# [M] CVE-2021-27363

## Summary
Severity: Medium
Advisory: CVE-2021-27363
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2021-03-07
Source: https://osv.dev/vulnerability/CVE-2021-27363
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.3. A kernel pointer leak can be used to determine the address of the iscsi_transport structure. When an iSCSI transport is registered with the iSCSI subsystem, the transport's handle is available to unprivileged users via the sysfs file system, at /sys/class/iscsi_transport/$TRANSPORT_NAME/handle. When read, the show_transport_handle function (in drivers/scsi/scsi_transport_iscsi.c) is called, which leaks the handle. This handle is actually the pointer to an iscsi_transport struct in the kernel module's global variables.

## References
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://security.netapp.com/advisory/ntap-20210409-0001/
- http://packetstormsecurity.com/files/162117/Kernel-Live-Patch-Security-Notice-LSN-0075-1.html
- https://bugzilla.suse.com/show_bug.cgi?id=1182716
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=688e8128b7a92df982709a4137ea4588d16f24aa
- http://www.openwall.com/lists/oss-security/2021/03/06/1
- https://blog.grimm-co.com/2021/03/new-old-bugs-in-linux-kernel.html
