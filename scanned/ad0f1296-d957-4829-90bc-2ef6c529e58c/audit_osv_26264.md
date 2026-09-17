# [M] rpmsg: virtio: Free driver_override when rpmsg_remove()

## Summary
Severity: Medium
Advisory: CVE-2023-52670
Ecosystem: Linux
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52670
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rpmsg: virtio: Free driver_override when rpmsg_remove()

Free driver_override when rpmsg_remove(), otherwise
the following memory leak will occur:

unreferenced object 0xffff0000d55d7080 (size 128):
  comm "kworker/u8:2", pid 56, jiffies 4294893188 (age 214.272s)
  hex dump (first 32 bytes):
    72 70 6d 73 67 5f 6e 73 00 00 00 00 00 00 00 00  rpmsg_ns........
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<000000009c94c9c1>] __kmem_cache_alloc_node+0x1f8/0x320
    [<000000002300d89b>] __kmalloc_node_track_caller+0x44/0x70
    [<00000000228a60c3>] kstrndup+0x4c/0x90
    [<0000000077158695>] driver_set_override+0xd0/0x164
    [<000000003e9c4ea5>] rpmsg_register_device_override+0x98/0x170
    [<000000001c0c89a8>] rpmsg_ns_register_device+0x24/0x30
    [<000000008bbf8fa2>] rpmsg_probe+0x2e0/0x3ec
    [<00000000e65a68df>] virtio_dev_probe+0x1c0/0x280
    [<00000000443331cc>] really_probe+0xbc/0x2dc
    [<00000000391064b1>] __driver_probe_device+0x78/0xe0
    [<00000000a41c9a5b>] driver_probe_device+0xd8/0x160
    [<000000009c3bd5df>] __device_attach_driver+0xb8/0x140
    [<0000000043cd7614>] bus_for_each_drv+0x7c/0xd4
    [<000000003b929a36>] __device_attach+0x9c/0x19c
    [<00000000a94e0ba8>] device_initial_probe+0x14/0x20
    [<000000003c999637>] bus_probe_device+0xa0/0xac

## References
- https://git.kernel.org/stable/c/229ce47cbfdc7d3a9415eb676abbfb77d676cb08
- https://git.kernel.org/stable/c/2d27a7b19cb354c6d04bcdc9239e261ff29858d6
- https://git.kernel.org/stable/c/4e6cef3fae5c164968118a13f3fe293700adc81a
- https://git.kernel.org/stable/c/69ca89d80f2c8a1f5af429b955637beea7eead30
- https://git.kernel.org/stable/c/9a416d624e5fb7246ea97c11fbfea7e0e27abf43
- https://git.kernel.org/stable/c/d5362c37e1f8a40096452fc201c30e705750e687
- https://git.kernel.org/stable/c/dd50fe18c234bd5ff22f658f4d414e8fa8cd6a5d
- https://git.kernel.org/stable/c/f4bb1d5daf77b1a95a43277268adf0d1430c2346
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52670.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
