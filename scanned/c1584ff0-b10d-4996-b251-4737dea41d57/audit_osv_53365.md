# [M] CVE-2022-41218

## Summary
Severity: Medium
Advisory: CVE-2022-41218
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-41218
Type: osv

## Details
In drivers/media/dvb-core/dmxdev.c in the Linux kernel through 5.19.10, there is a use-after-free caused by refcount races, affecting dvb_demux_open and dvb_dmxdev_release.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lore.kernel.org/all/20220908132754.30532-1-tiwai%40suse.de/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=fd3d91ab1c6ab0628fe642dd570b56302c30a792
- https://www.debian.org/security/2023/dsa-5324
- http://www.openwall.com/lists/oss-security/2022/09/24/2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/drivers/media/dvb-core/dmxdev.c
- http://www.openwall.com/lists/oss-security/2022/09/23/4
- http://www.openwall.com/lists/oss-security/2022/09/24/1
