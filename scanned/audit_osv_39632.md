# [H] dm: fix unlocked test for dm_suspended_md

## Summary
Severity: High
Advisory: CVE-2026-46327
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46327
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.75, >=6.13.0 <6.18.14, >=6.16.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: fix unlocked test for dm_suspended_md

The function dm_blk_report_zones tests if the device is suspended with
the "dm_suspended_md" call. However, this function is called without
holding any locks, so the device may be suspended just after it.

Move the call to dm_suspended_md after dm_get_live_table, so that the
device can't be suspended after the suspended state was tested.

## References
- https://git.kernel.org/stable/c/175ac0a6115400278d3900f5a04a58b17b3f6cd0
- https://git.kernel.org/stable/c/24c405fdbe215c45e57bba672cc42859038491ee
- https://git.kernel.org/stable/c/7a3385e97af2b6f485fef11e82d8c29adee4be93
- https://git.kernel.org/stable/c/d809a36692ee1394cac85ce6ba7cf8ea58da5812
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46327.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46327
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
