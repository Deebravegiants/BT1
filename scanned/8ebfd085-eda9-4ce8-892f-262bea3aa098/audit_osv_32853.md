# [H] dm: fix dm_blk_report_zones

## Summary
Severity: High
Advisory: CVE-2025-38141
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38141
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: fix dm_blk_report_zones

If dm_get_live_table() returned NULL, dm_put_live_table() was never
called. Also, it is possible that md->zone_revalidate_map will change
while calling this function. Only read it once, so that we are always
using the same value. Otherwise we might miss a call to
dm_put_live_table().

Finally, while md->zone_revalidate_map is set and a process is calling
blk_revalidate_disk_zones() to set up the zone append emulation
resources, it is possible that another process, perhaps triggered by
blkdev_report_zones_ioctl(), will call dm_blk_report_zones(). If
blk_revalidate_disk_zones() fails, these resources can be freed while
the other process is still using them, causing a use-after-free error.

blk_revalidate_disk_zones() will only ever be called when initially
setting up the zone append emulation resources, such as when setting up
a zoned dm-crypt table for the first time. Further table swaps will not
set md->zone_revalidate_map or call blk_revalidate_disk_zones().
However it must be called using the new table (referenced by
md->zone_revalidate_map) and the new queue limits while the DM device is
suspended. dm_blk_report_zones() needs some way to distinguish between a
call from blk_revalidate_disk_zones(), which must be allowed to use
md->zone_revalidate_map to access this not yet activated table, and all
other calls to dm_blk_report_zones(), which should not be allowed while
the device is suspended and cannot use md->zone_revalidate_map, since
the zone resources might be freed by the process currently calling
blk_revalidate_disk_zones().

Solve this by tracking the process that sets md->zone_revalidate_map in
dm_revalidate_zones() and only allowing that process to make use of it
in dm_blk_report_zones().

## References
- https://git.kernel.org/stable/c/37f53a2c60d03743e0eacf7a0c01c279776fef4e
- https://git.kernel.org/stable/c/d19bc1b4dd5f322980b1f05f79b2ea4f0db10920
- https://git.kernel.org/stable/c/f9c1bdf24615303d48a2d0fd629c88f3189563aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38141.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
