# [H] btrfs: fix double free in create_space_info() error path

## Summary
Severity: High
Advisory: CVE-2026-46129
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46129
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix double free in create_space_info() error path

When kobject_init_and_add() fails, the call chain is:

create_space_info()
-> btrfs_sysfs_add_space_info_type()
-> kobject_init_and_add()
-> failure
-> kobject_put(&space_info->kobj)
-> space_info_release()
-> kfree(space_info)

Then control returns to create_space_info():

btrfs_sysfs_add_space_info_type() returns error
-> goto out_free
-> kfree(space_info)

This causes a double free.

Keep the direct kfree(space_info) for the earlier failure path, but
after btrfs_sysfs_add_space_info_type() has called kobject_put(), let
the kobject release callback handle the cleanup.

## References
- https://git.kernel.org/stable/c/3f487be81292702a59ea9dbc4088b3360a50e837
- https://git.kernel.org/stable/c/9a060970fd7b5e1c561e4ce73cb9949e4269a738
- https://git.kernel.org/stable/c/ae6d6e31ceb72b7697c28a528e4923c08e3c2ef5
- https://git.kernel.org/stable/c/c2670ec4aa49ca226bce9776601e0da37502be07
- https://git.kernel.org/stable/c/dd6ade0fdd59218d71a981ae7c937a304e49209c
- https://git.kernel.org/stable/c/f414b3abbba59ef379a2b3c31f2bdd9358ed5e53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46129.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
