# [H] CVE-2023-35824

## Summary
Severity: High
Advisory: CVE-2023-35824
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-18
Source: https://osv.dev/vulnerability/CVE-2023-35824
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.2. A use-after-free was found in dm1105_remove in drivers/media/pci/dm1105/dm1105.c.

## References
- https://lore.kernel.org/all/49bb0b6a-e669-d4e7-d742-a19d2763e947%40xs4all.nl/
- https://lore.kernel.org/lkml/20230318081506.795147-1-zyytlz.wz%40163.com/
- https://security.netapp.com/advisory/ntap-20230803-0002/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5abda7a16698d4d1f47af1168d8fa2c640116b4a
