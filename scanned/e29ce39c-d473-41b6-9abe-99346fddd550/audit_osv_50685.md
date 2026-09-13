# [H] CVE-2020-28374

## Summary
Severity: High
Advisory: CVE-2020-28374
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-01-13
Source: https://osv.dev/vulnerability/CVE-2020-28374
Type: osv

## Details
In drivers/target/target_core_xcopy.c in the Linux kernel before 5.10.7, insufficient identifier checking in the LIO SCSI target code can be used by remote attackers to read or write files via directory traversal in an XCOPY request, aka CID-2896c93811e3. For example, an attack can occur over a network if the attacker has access to one iSCSI LUN. The attacker gains control over file access because I/O operations are proxied via an attacker-selected backstore.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LTGQDYIEO2GOCOOKADBHEITF44GY55QF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HK7SRTITN5ABAUOOIGFVR7XE5YKYYAVO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FZEUPID5DZYLZBIO4BEVLHFUDZZIFL57/
- http://www.openwall.com/lists/oss-security/2021/01/13/2
- http://www.openwall.com/lists/oss-security/2021/01/13/5
- http://packetstormsecurity.com/files/161229/Kernel-Live-Patch-Security-Notice-LSN-0074-1.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://www.debian.org/security/2021/dsa-4843
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.7
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://security.netapp.com/advisory/ntap-20210219-0002/
- https://bugzilla.suse.com/attachment.cgi?id=844938
- https://bugzilla.suse.com/show_bug.cgi?id=1178372
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2896c93811e39d63a4d9b63ccf12a8fbc226e5e4
- https://github.com/torvalds/linux/commit/2896c93811e39d63a4d9b63ccf12a8fbc226e5e4
