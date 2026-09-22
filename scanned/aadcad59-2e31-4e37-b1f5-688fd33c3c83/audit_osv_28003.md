# [H] s390/zcrypt: fix reference counting on zcrypt card objects

## Summary
Severity: High
Advisory: CVE-2024-26957
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26957
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: fix reference counting on zcrypt card objects

Tests with hot-plugging crytpo cards on KVM guests with debug
kernel build revealed an use after free for the load field of
the struct zcrypt_card. The reason was an incorrect reference
handling of the zcrypt card object which could lead to a free
of the zcrypt card object while it was still in use.

This is an example of the slab message:

    kernel: 0x00000000885a7512-0x00000000885a7513 @offset=1298. First byte 0x68 instead of 0x6b
    kernel: Allocated in zcrypt_card_alloc+0x36/0x70 [zcrypt] age=18046 cpu=3 pid=43
    kernel:  kmalloc_trace+0x3f2/0x470
    kernel:  zcrypt_card_alloc+0x36/0x70 [zcrypt]
    kernel:  zcrypt_cex4_card_probe+0x26/0x380 [zcrypt_cex4]
    kernel:  ap_device_probe+0x15c/0x290
    kernel:  really_probe+0xd2/0x468
    kernel:  driver_probe_device+0x40/0xf0
    kernel:  __device_attach_driver+0xc0/0x140
    kernel:  bus_for_each_drv+0x8c/0xd0
    kernel:  __device_attach+0x114/0x198
    kernel:  bus_probe_device+0xb4/0xc8
    kernel:  device_add+0x4d2/0x6e0
    kernel:  ap_scan_adapter+0x3d0/0x7c0
    kernel:  ap_scan_bus+0x5a/0x3b0
    kernel:  ap_scan_bus_wq_callback+0x40/0x60
    kernel:  process_one_work+0x26e/0x620
    kernel:  worker_thread+0x21c/0x440
    kernel: Freed in zcrypt_card_put+0x54/0x80 [zcrypt] age=9024 cpu=3 pid=43
    kernel:  kfree+0x37e/0x418
    kernel:  zcrypt_card_put+0x54/0x80 [zcrypt]
    kernel:  ap_device_remove+0x4c/0xe0
    kernel:  device_release_driver_internal+0x1c4/0x270
    kernel:  bus_remove_device+0x100/0x188
    kernel:  device_del+0x164/0x3c0
    kernel:  device_unregister+0x30/0x90
    kernel:  ap_scan_adapter+0xc8/0x7c0
    kernel:  ap_scan_bus+0x5a/0x3b0
    kernel:  ap_scan_bus_wq_callback+0x40/0x60
    kernel:  process_one_work+0x26e/0x620
    kernel:  worker_thread+0x21c/0x440
    kernel:  kthread+0x150/0x168
    kernel:  __ret_from_fork+0x3c/0x58
    kernel:  ret_from_fork+0xa/0x30
    kernel: Slab 0x00000372022169c0 objects=20 used=18 fp=0x00000000885a7c88 flags=0x3ffff00000000a00(workingset|slab|node=0|zone=1|lastcpupid=0x1ffff)
    kernel: Object 0x00000000885a74b8 @offset=1208 fp=0x00000000885a7c88
    kernel: Redzone  00000000885a74b0: bb bb bb bb bb bb bb bb                          ........
    kernel: Object   00000000885a74b8: 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b  kkkkkkkkkkkkkkkk
    kernel: Object   00000000885a74c8: 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b  kkkkkkkkkkkkkkkk
    kernel: Object   00000000885a74d8: 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b  kkkkkkkkkkkkkkkk
    kernel: Object   00000000885a74e8: 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b  kkkkkkkkkkkkkkkk
    kernel: Object   00000000885a74f8: 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b  kkkkkkkkkkkkkkkk
    kernel: Object   00000000885a7508: 6b 6b 6b 6b 6b 6b 6b 6b 6b 6b 68 4b 6b 6b 6b a5  kkkkkkkkkkhKkkk.
    kernel: Redzone  00000000885a7518: bb bb bb bb bb bb bb bb                          ........
    kernel: Padding  00000000885a756c: 5a 5a 5a 5a 5a 5a 5a 5a 5a 5a 5a 5a              ZZZZZZZZZZZZ
    kernel: CPU: 0 PID: 387 Comm: systemd-udevd Not tainted 6.8.0-HF #2
    kernel: Hardware name: IBM 3931 A01 704 (KVM/Linux)
    kernel: Call Trace:
    kernel:  [<00000000ca5ab5b8>] dump_stack_lvl+0x90/0x120
    kernel:  [<00000000c99d78bc>] check_bytes_and_report+0x114/0x140
    kernel:  [<00000000c99d53cc>] check_object+0x334/0x3f8
    kernel:  [<00000000c99d820c>] alloc_debug_processing+0xc4/0x1f8
    kernel:  [<00000000c99d852e>] get_partial_node.part.0+0x1ee/0x3e0
    kernel:  [<00000000c99d94ec>] ___slab_alloc+0xaf4/0x13c8
    kernel:  [<00000000c99d9e38>] __slab_alloc.constprop.0+0x78/0xb8
    kernel:  [<00000000c99dc8dc>] __kmalloc+0x434/0x590
    kernel:  [<00000000c9b4c0ce>] ext4_htree_store_dirent+0x4e/0x1c0
    kernel:  [<00000000c9b908a2>] htree_dirblock_to_tree+0x17a/0x3f0
    kernel: 
---truncated---

## References
- https://git.kernel.org/stable/c/394b6d8bbdf9ddee6d5bcf3e1f3e9f23eecd6484
- https://git.kernel.org/stable/c/50ed48c80fecbe17218afed4f8bed005c802976c
- https://git.kernel.org/stable/c/6470078ab3d8f222115e11c4ec67351f3031b3dd
- https://git.kernel.org/stable/c/7e500849fa558879a1cde43f80c7c048c2437058
- https://git.kernel.org/stable/c/9daddee03de3f231012014dab8ab2b277a116a55
- https://git.kernel.org/stable/c/a55677878b93e9ebc31f66d0e2fb93be5e7836a6
- https://git.kernel.org/stable/c/a64ab862e84e3e698cd351a87cdb504c7fc575ca
- https://git.kernel.org/stable/c/b7f6c3630eb3f103115ab0d7613588064f665d0d
- https://git.kernel.org/stable/c/befb7f889594d23e1b475720cf93efd2f77df000
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26957.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26957
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
