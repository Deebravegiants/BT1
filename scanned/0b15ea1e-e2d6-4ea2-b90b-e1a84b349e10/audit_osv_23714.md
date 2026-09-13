# [M] scsi: sd: Fix potential NULL pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2022-49376
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49376
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: sd: Fix potential NULL pointer dereference

If sd_probe() sees an early error before sdkp->device is initialized,
sd_zbc_release_disk() is called. This causes a NULL pointer dereference
when sd_is_zoned() is called inside that function. Avoid this by removing
the call to sd_zbc_release_disk() in sd_probe() error path.

This change is safe and does not result in zone information memory leakage
because the zone information for a zoned disk is allocated only when
sd_revalidate_disk() is called, at which point sdkp->disk_dev is fully set,
resulting in sd_disk_release() being called when needed to cleanup a disk
zone information using sd_zbc_release_disk().

## References
- https://git.kernel.org/stable/c/05fbde3a77a4f1d62e4c4428f384288c1f1a0be5
- https://git.kernel.org/stable/c/0fcb0b131cc90c8f523a293d84c58d0c7273c96f
- https://git.kernel.org/stable/c/3733439593ad12f7b54ae35c273ea6f15d692de3
- https://git.kernel.org/stable/c/78f8e96df06e2d04d82d4071c299b59d28744f47
- https://git.kernel.org/stable/c/c1f0187025905e9981000d44a92e159468b561a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49376.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49376
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
