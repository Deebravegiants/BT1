# [H] CVE-2023-35826

## Summary
Severity: High
Advisory: CVE-2023-35826
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-18
Source: https://osv.dev/vulnerability/CVE-2023-35826
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.2. A use-after-free was found in cedrus_remove in drivers/staging/media/sunxi/cedrus/cedrus.c.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=50d0a7aea4809cef87979d4669911276aa23b71f
- https://lore.kernel.org/all/a4dafa22-3ee3-dbe1-fd50-fee07883ce1a%40xs4all.nl/
- https://security.netapp.com/advisory/ntap-20230803-0002/
- https://lore.kernel.org/linux-arm-kernel/20230308032333.1893394-1-zyytlz.wz%40163.com/T/
