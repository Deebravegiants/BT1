# [H] block: RCU protect disk->conv_zones_bitmap

## Summary
Severity: High
Advisory: CVE-2024-57875
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57875
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: RCU protect disk->conv_zones_bitmap

Ensure that a disk revalidation changing the conventional zones bitmap
of a disk does not cause invalid memory references when using the
disk_zone_is_conv() helper by RCU protecting the disk->conv_zones_bitmap
pointer.

disk_zone_is_conv() is modified to operate under the RCU read lock and
the function disk_set_conv_zones_bitmap() is added to update a disk
conv_zones_bitmap pointer using rcu_replace_pointer() with the disk
zone_wplugs_lock spinlock held.

disk_free_zone_resources() is modified to call
disk_update_zone_resources() with a NULL bitmap pointer to free the disk
conv_zones_bitmap. disk_set_conv_zones_bitmap() is also used in
disk_update_zone_resources() to set the new (revalidated) bitmap and
free the old one.

## References
- https://git.kernel.org/stable/c/493326c4f10cc71a42c27fdc97ce112182ee4cbc
- https://git.kernel.org/stable/c/d7cb6d7414ea1b33536fa6d11805cb8dceec1f97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57875.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57875
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
