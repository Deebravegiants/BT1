# [H] CVE-2023-35823

## Summary
Severity: High
Advisory: CVE-2023-35823
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-18
Source: https://osv.dev/vulnerability/CVE-2023-35823
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.2. A use-after-free was found in saa7134_finidev in drivers/media/pci/saa7134/saa7134-core.c.

## References
- https://lore.kernel.org/lkml/20230318085023.832510-1-zyytlz.wz%40163.com/t/
- https://lore.kernel.org/all/49bb0b6a-e669-d4e7-d742-a19d2763e947%40xs4all.nl/
- https://security.netapp.com/advisory/ntap-20230803-0002/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=30cf57da176cca80f11df0d9b7f71581fe601389
