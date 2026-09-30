# [H] btrfs: fix double free in create_space_info_sub_group() error path

## Summary
Severity: High
Advisory: CVE-2026-46164
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46164
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.176, >=6.2.0 <6.6.141, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.16.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix double free in create_space_info_sub_group() error path

When kobject_init_and_add() fails, the call chain is:

create_space_info_sub_group()
-> btrfs_sysfs_add_space_info_type()
-> kobject_init_and_add()
-> failure
-> kobject_put(&sub_group->kobj)
-> space_info_release()
-> kfree(sub_group)

Then control returns to create_space_info_sub_group(), where:

btrfs_sysfs_add_space_info_type() returns error
-> kfree(sub_group)

Thus, sub_group is freed twice.

Keep parent->sub_group[index] = NULL for the failure path, but after
btrfs_sysfs_add_space_info_type() has called kobject_put(), let the
kobject release callback handle the cleanup.

## References
- https://git.kernel.org/stable/c/14b22be1dd844383eb03af9b1ee3b6b25d32aeaf
- https://git.kernel.org/stable/c/259af6857a1b4f1e9ef8b780353f9d11c26a22bd
- https://git.kernel.org/stable/c/a7449edf96143f192606ec8647e3167e1ecbd728
- https://git.kernel.org/stable/c/c2d59527cba6d59f0d77a75c1101ab4e69758bea
- https://git.kernel.org/stable/c/d2a675f2e238ec96c8e91e2718c1f910c9c8fb21
- https://git.kernel.org/stable/c/dfd05a16b5c9d1d98b47905f37f2fccda52173d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46164.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46164
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
