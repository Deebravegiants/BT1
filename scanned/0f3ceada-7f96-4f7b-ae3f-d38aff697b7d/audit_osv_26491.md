# [M] ubi: Fix unreferenced object reported by kmemleak in ubi_resize_volume()

## Summary
Severity: Medium
Advisory: CVE-2023-53271
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53271
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubi: Fix unreferenced object reported by kmemleak in ubi_resize_volume()

There is a memory leaks problem reported by kmemleak:

unreferenced object 0xffff888102007a00 (size 128):
  comm "ubirsvol", pid 32090, jiffies 4298464136 (age 2361.231s)
  hex dump (first 32 bytes):
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff  ................
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff  ................
  backtrace:
[<ffffffff8176cecd>] __kmalloc+0x4d/0x150
[<ffffffffa02a9a36>] ubi_eba_create_table+0x76/0x170 [ubi]
[<ffffffffa029764e>] ubi_resize_volume+0x1be/0xbc0 [ubi]
[<ffffffffa02a3321>] ubi_cdev_ioctl+0x701/0x1850 [ubi]
[<ffffffff81975d2d>] __x64_sys_ioctl+0x11d/0x170
[<ffffffff83c142a5>] do_syscall_64+0x35/0x80
[<ffffffff83e0006a>] entry_SYSCALL_64_after_hwframe+0x46/0xb0

This is due to a mismatch between create and destroy interfaces, and
in detail that "new_eba_tbl" created by ubi_eba_create_table() but
destroyed by kfree(), while will causing "new_eba_tbl->entries" not
freed.

Fix it by replacing kfree(new_eba_tbl) with
ubi_eba_destroy_table(new_eba_tbl)

## References
- https://git.kernel.org/stable/c/07b60f7452d2fa731737552937cb81821919f874
- https://git.kernel.org/stable/c/09780a44093b53f9cbca76246af2e4ff0884e512
- https://git.kernel.org/stable/c/1e591ea072df7211f64542a09482b5f81cb3ad27
- https://git.kernel.org/stable/c/26ec2d66aecab8ff997b912c20247fedba4f5740
- https://git.kernel.org/stable/c/27b760b81951d8d5e5c952a696af8574052b0709
- https://git.kernel.org/stable/c/31d60afe2cc2b712dbefcaab6b7d6a47036f844e
- https://git.kernel.org/stable/c/5c0c81a313492b83bd0c038b8839b0e04eb87563
- https://git.kernel.org/stable/c/95a72417dd13ebcdcb1bd0c5d4d15f7c5bfbb288
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53271.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53271
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
