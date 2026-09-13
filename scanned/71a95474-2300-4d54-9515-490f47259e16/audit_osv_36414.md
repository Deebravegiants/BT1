# [H] mshv: Fix use-after-free in mshv_map_user_memory error path

## Summary
Severity: High
Advisory: CVE-2026-23432
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23432
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mshv: Fix use-after-free in mshv_map_user_memory error path

In the error path of mshv_map_user_memory(), calling vfree() directly on
the region leaves the MMU notifier registered. When userspace later unmaps
the memory, the notifier fires and accesses the freed region, causing a
use-after-free and potential kernel panic.

Replace vfree() with mshv_partition_put() to properly unregister
the MMU notifier before freeing the region.

## References
- https://git.kernel.org/stable/c/34861bdc0c0196b6c2dd48f7454029407704ff6e
- https://git.kernel.org/stable/c/6922db250422a0dfee34de322f86b7a73d713d33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23432
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
