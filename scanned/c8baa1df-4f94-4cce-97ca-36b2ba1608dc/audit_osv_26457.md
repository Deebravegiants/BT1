# [M] watchdog: Fix kmemleak in watchdog_cdev_register

## Summary
Severity: Medium
Advisory: CVE-2023-53234
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53234
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.15.100, >=5.11.0 <6.1.18, >=5.16.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

watchdog: Fix kmemleak in watchdog_cdev_register

kmemleak reports memory leaks in watchdog_dev_register, as follows:
unreferenced object 0xffff888116233000 (size 2048):
  comm ""modprobe"", pid 28147, jiffies 4353426116 (age 61.741s)
  hex dump (first 32 bytes):
    80 fa b9 05 81 88 ff ff 08 30 23 16 81 88 ff ff  .........0#.....
    08 30 23 16 81 88 ff ff 00 00 00 00 00 00 00 00  .0#.............
  backtrace:
    [<000000007f001ffd>] __kmem_cache_alloc_node+0x157/0x220
    [<000000006a389304>] kmalloc_trace+0x21/0x110
    [<000000008d640eea>] watchdog_dev_register+0x4e/0x780 [watchdog]
    [<0000000053c9f248>] __watchdog_register_device+0x4f0/0x680 [watchdog]
    [<00000000b2979824>] watchdog_register_device+0xd2/0x110 [watchdog]
    [<000000001f730178>] 0xffffffffc10880ae
    [<000000007a1a8bcc>] do_one_initcall+0xcb/0x4d0
    [<00000000b98be325>] do_init_module+0x1ca/0x5f0
    [<0000000046d08e7c>] load_module+0x6133/0x70f0
    ...

unreferenced object 0xffff888105b9fa80 (size 16):
  comm ""modprobe"", pid 28147, jiffies 4353426116 (age 61.741s)
  hex dump (first 16 bytes):
    77 61 74 63 68 64 6f 67 31 00 b9 05 81 88 ff ff  watchdog1.......
  backtrace:
    [<000000007f001ffd>] __kmem_cache_alloc_node+0x157/0x220
    [<00000000486ab89b>] __kmalloc_node_track_caller+0x44/0x1b0
    [<000000005a39aab0>] kvasprintf+0xb5/0x140
    [<0000000024806f85>] kvasprintf_const+0x55/0x180
    [<000000009276cb7f>] kobject_set_name_vargs+0x56/0x150
    [<00000000a92e820b>] dev_set_name+0xab/0xe0
    [<00000000cec812c6>] watchdog_dev_register+0x285/0x780 [watchdog]
    [<0000000053c9f248>] __watchdog_register_device+0x4f0/0x680 [watchdog]
    [<00000000b2979824>] watchdog_register_device+0xd2/0x110 [watchdog]
    [<000000001f730178>] 0xffffffffc10880ae
    [<000000007a1a8bcc>] do_one_initcall+0xcb/0x4d0
    [<00000000b98be325>] do_init_module+0x1ca/0x5f0
    [<0000000046d08e7c>] load_module+0x6133/0x70f0
    ...

The reason is that put_device is not be called if cdev_device_add fails
and wdd->id != 0.

watchdog_cdev_register
  wd_data = kzalloc                             [1]
  err = dev_set_name                            [2]
  ..
  err = cdev_device_add
  if (err) {
    if (wdd->id == 0) {  // wdd->id != 0
      ..
    }
    return err;  // [1],[2] would be leaked

To fix it, call put_device in all wdd->id cases.

## References
- https://git.kernel.org/stable/c/13721a2ac66b246f5802ba1b75ad8637e53eeecc
- https://git.kernel.org/stable/c/23cc41c3f19c4d858c3708f1c0a06e94958e6c3b
- https://git.kernel.org/stable/c/50808d034e199fe3ff7a9d2068a4eebeb6b4098a
- https://git.kernel.org/stable/c/59e391b3fc507a15b7e8e9d9f4de87cae177c366
- https://git.kernel.org/stable/c/8c1655600f4f2839fb844fe8c70b2b65fadc7a56
- https://git.kernel.org/stable/c/ac099d94e0480c937aa9172ab64074981ca1a4d3
- https://git.kernel.org/stable/c/bf26b0e430ce34261f45959989edaf680b64d538
- https://git.kernel.org/stable/c/c5a21a5501508ae3afa2fe6d5a3e74a37fa48df3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53234.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
