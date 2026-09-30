# [H] CVE-2016-10905

## Summary
Severity: High
Advisory: CVE-2016-10905
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2016-10905
Type: osv

## Details
An issue was discovered in fs/gfs2/rgrp.c in the Linux kernel before 4.8. A use-after-free is caused by the functions gfs2_clear_rgrpd and read_rindex_entry.

## References
- https://support.f5.com/csp/article/K31332013?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4145-1/
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://seclists.org/bugtraq/2019/Nov/11
- https://support.f5.com/csp/article/K31332013
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=36e4ad0316c017d5b271378ed9a1c9a4b77fab5f
