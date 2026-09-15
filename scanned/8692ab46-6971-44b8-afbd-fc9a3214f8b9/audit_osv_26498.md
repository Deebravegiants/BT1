# [M] ubifs: Fix memory leak in ubifs_sysfs_init()

## Summary
Severity: Medium
Advisory: CVE-2023-53278
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53278
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: Fix memory leak in ubifs_sysfs_init()

When insmod ubifs.ko, a kmemleak reported as below:

 unreferenced object 0xffff88817fb1a780 (size 8):
   comm "insmod", pid 25265, jiffies 4295239702 (age 100.130s)
   hex dump (first 8 bytes):
     75 62 69 66 73 00 ff ff                          ubifs...
   backtrace:
     [<ffffffff81b3fc4c>] slab_post_alloc_hook+0x9c/0x3c0
     [<ffffffff81b44bf3>] __kmalloc_track_caller+0x183/0x410
     [<ffffffff8198d3da>] kstrdup+0x3a/0x80
     [<ffffffff8198d486>] kstrdup_const+0x66/0x80
     [<ffffffff83989325>] kvasprintf_const+0x155/0x190
     [<ffffffff83bf55bb>] kobject_set_name_vargs+0x5b/0x150
     [<ffffffff83bf576b>] kobject_set_name+0xbb/0xf0
     [<ffffffff8100204c>] do_one_initcall+0x14c/0x5a0
     [<ffffffff8157e380>] do_init_module+0x1f0/0x660
     [<ffffffff815857be>] load_module+0x6d7e/0x7590
     [<ffffffff8158644f>] __do_sys_finit_module+0x19f/0x230
     [<ffffffff815866b3>] __x64_sys_finit_module+0x73/0xb0
     [<ffffffff88c98e85>] do_syscall_64+0x35/0x80
     [<ffffffff88e00087>] entry_SYSCALL_64_after_hwframe+0x63/0xcd

When kset_register() failed, we should call kset_put to cleanup it.

## References
- https://git.kernel.org/stable/c/1c5fdf2d4647219d2267ccb08c7f2c7095bf3450
- https://git.kernel.org/stable/c/203a55f04f66eea1a1ca7e5a302a7f5c99c62327
- https://git.kernel.org/stable/c/d42c2b18c42da7378e67b6414aafe93b65de89d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53278.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53278
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
