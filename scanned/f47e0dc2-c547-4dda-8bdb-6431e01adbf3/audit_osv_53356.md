# [M] CVE-2022-40768

## Summary
Severity: Medium
Advisory: CVE-2022-40768
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-18
Source: https://osv.dev/vulnerability/CVE-2022-40768
Type: osv

## Details
drivers/scsi/stex.c in the Linux kernel through 5.19.9 allows local users to obtain sensitive information from kernel memory because stex_queuecommand_lck lacks a memset for the PASSTHRU_CMD case.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6022f210461fef67e6e676fd8544ca02d1bcfa7a
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lore.kernel.org/all/20220908145154.2284098-1-gregkh%40linuxfoundation.org/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/drivers/scsi/stex.c
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- http://www.openwall.com/lists/oss-security/2022/09/19/1
- https://www.openwall.com/lists/oss-security/2022/09/09/1
