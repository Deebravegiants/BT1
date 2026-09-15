# [M] drm/imagination: avoid deadlock on fence release

## Summary
Severity: Medium
Advisory: CVE-2025-21911
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21911
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/imagination: avoid deadlock on fence release

Do scheduler queue fence release processing on a workqueue, rather
than in the release function itself.

Fixes deadlock issues such as the following:

[  607.400437] ============================================
[  607.405755] WARNING: possible recursive locking detected
[  607.415500] --------------------------------------------
[  607.420817] weston:zfq0/24149 is trying to acquire lock:
[  607.426131] ffff000017d041a0 (reservation_ww_class_mutex){+.+.}-{3:3}, at: pvr_gem_object_vunmap+0x40/0xc0 [powervr]
[  607.436728]
               but task is already holding lock:
[  607.442554] ffff000017d105a0 (reservation_ww_class_mutex){+.+.}-{3:3}, at: dma_buf_ioctl+0x250/0x554
[  607.451727]
               other info that might help us debug this:
[  607.458245]  Possible unsafe locking scenario:

[  607.464155]        CPU0
[  607.466601]        ----
[  607.469044]   lock(reservation_ww_class_mutex);
[  607.473584]   lock(reservation_ww_class_mutex);
[  607.478114]
                *** DEADLOCK ***

## References
- https://git.kernel.org/stable/c/9bd8b8d34cf4efba18766d64f817c819ed1bbde7
- https://git.kernel.org/stable/c/d993ae7360923efd6ade43a32043459a121c28c1
- https://git.kernel.org/stable/c/df1a1ed5e1bdd9cc13148e0e5549f5ebcf76cf13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21911.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
