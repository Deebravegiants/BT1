# [H] CVE-2023-35829

## Summary
Severity: High
Advisory: CVE-2023-35829
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-18
Source: https://osv.dev/vulnerability/CVE-2023-35829
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.2. A use-after-free was found in rkvdec_remove in drivers/staging/media/rkvdec/rkvdec.c.

## References
- https://lore.kernel.org/all/a4dafa22-3ee3-dbe1-fd50-fee07883ce1a%40xs4all.nl/
- https://lore.kernel.org/lkml/20230307173900.1299387-1-zyytlz.wz%40163.com/T/
- https://security.netapp.com/advisory/ntap-20230803-0002/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3228cec23b8b29215e18090c6ba635840190993d
