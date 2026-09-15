# [M] vduse: Fix NULL pointer dereference on sysfs access

## Summary
Severity: Medium
Advisory: CVE-2022-49329
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49329
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

vduse: Fix NULL pointer dereference on sysfs access

The control device has no drvdata. So we will get a
NULL pointer dereference when accessing control
device's msg_timeout attribute via sysfs:

[ 132.841881][ T3644] BUG: kernel NULL pointer dereference, address: 00000000000000f8
[ 132.850619][ T3644] RIP: 0010:msg_timeout_show (drivers/vdpa/vdpa_user/vduse_dev.c:1271)
[ 132.869447][ T3644] dev_attr_show (drivers/base/core.c:2094)
[ 132.870215][ T3644] sysfs_kf_seq_show (fs/sysfs/file.c:59)
[ 132.871164][ T3644] ? device_remove_bin_file (drivers/base/core.c:2088)
[ 132.872082][ T3644] kernfs_seq_show (fs/kernfs/file.c:164)
[ 132.872838][ T3644] seq_read_iter (fs/seq_file.c:230)
[ 132.873578][ T3644] ? __vmalloc_area_node (mm/vmalloc.c:3041)
[ 132.874532][ T3644] kernfs_fop_read_iter (fs/kernfs/file.c:238)
[ 132.875513][ T3644] __kernel_read (fs/read_write.c:440 (discriminator 1))
[ 132.876319][ T3644] kernel_read (fs/read_write.c:459)
[ 132.877129][ T3644] kernel_read_file (fs/kernel_read_file.c:94)
[ 132.877978][ T3644] kernel_read_file_from_fd (include/linux/file.h:45 fs/kernel_read_file.c:186)
[ 132.879019][ T3644] __do_sys_finit_module (kernel/module.c:4207)
[ 132.879930][ T3644] __ia32_sys_finit_module (kernel/module.c:4189)
[ 132.880930][ T3644] do_int80_syscall_32 (arch/x86/entry/common.c:112 arch/x86/entry/common.c:132)
[ 132.881847][ T3644] entry_INT80_compat (arch/x86/entry/entry_64_compat.S:419)

To fix it, don't create the unneeded attribute for
control device anymore.

## References
- https://git.kernel.org/stable/c/30fd1b56621e187346f65d01fe34870634b15188
- https://git.kernel.org/stable/c/3a7a81f4835dfda11f39fdd27586da14331896eb
- https://git.kernel.org/stable/c/b22fdee17ec62604060fb0fda5e1414b634666e1
- https://git.kernel.org/stable/c/b27ee76c74dc831d6e092eaebc2dfc9c0beed1c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49329.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49329
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
