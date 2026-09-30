# [M] CVE-2018-10021

## Summary
Severity: Medium
Advisory: CVE-2018-10021
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-11
Source: https://osv.dev/vulnerability/CVE-2018-10021
Type: osv

## Details
drivers/scsi/libsas/sas_scsi_host.c in the Linux kernel before 4.16 allows local users to cause a denial of service (ata qc leak) by triggering certain failure conditions. NOTE: a third party disputes the relevance of this report because the failure can only occur for physically proximate attackers who unplug SAS Host Bus Adapter cables

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3678-2/
- https://usn.ubuntu.com/3678-4/
- https://usn.ubuntu.com/3696-2/
- https://usn.ubuntu.com/3678-1/
- https://usn.ubuntu.com/3678-3/
- https://usn.ubuntu.com/3696-1/
- https://usn.ubuntu.com/3754-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=318aaf34f1179b39fa9c30fa0f3288b645beee39
- https://github.com/torvalds/linux/commit/318aaf34f1179b39fa9c30fa0f3288b645beee39
- https://bugzilla.suse.com/show_bug.cgi?id=1089281
