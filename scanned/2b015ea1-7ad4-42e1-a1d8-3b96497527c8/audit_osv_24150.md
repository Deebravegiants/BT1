# [M] net: hns: fix possible memory leak in hnae_ae_register()

## Summary
Severity: Medium
Advisory: CVE-2022-50352
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50352
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.9.332, >=4.10.0 <4.14.298, >=4.15.0 <4.19.264, >=4.20.0 <5.4.221, >=5.5.0 <5.10.152, >=5.11.0 <5.15.76, >=5.16.0 <6.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns: fix possible memory leak in hnae_ae_register()

Inject fault while probing module, if device_register() fails,
but the refcount of kobject is not decreased to 0, the name
allocated in dev_set_name() is leaked. Fix this by calling
put_device(), so that name can be freed in callback function
kobject_cleanup().

unreferenced object 0xffff00c01aba2100 (size 128):
  comm "systemd-udevd", pid 1259, jiffies 4294903284 (age 294.152s)
  hex dump (first 32 bytes):
    68 6e 61 65 30 00 00 00 18 21 ba 1a c0 00 ff ff  hnae0....!......
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<0000000034783f26>] slab_post_alloc_hook+0xa0/0x3e0
    [<00000000748188f2>] __kmem_cache_alloc_node+0x164/0x2b0
    [<00000000ab0743e8>] __kmalloc_node_track_caller+0x6c/0x390
    [<000000006c0ffb13>] kvasprintf+0x8c/0x118
    [<00000000fa27bfe1>] kvasprintf_const+0x60/0xc8
    [<0000000083e10ed7>] kobject_set_name_vargs+0x3c/0xc0
    [<000000000b87affc>] dev_set_name+0x7c/0xa0
    [<000000003fd8fe26>] hnae_ae_register+0xcc/0x190 [hnae]
    [<00000000fe97edc9>] hns_dsaf_ae_init+0x9c/0x108 [hns_dsaf]
    [<00000000c36ff1eb>] hns_dsaf_probe+0x548/0x748 [hns_dsaf]

## References
- https://git.kernel.org/stable/c/02dc0db19d944b4a90941db505ecf1aaec714be4
- https://git.kernel.org/stable/c/2974f3b330ef25f5d34a4948d04290c2cd7802cf
- https://git.kernel.org/stable/c/3b78453cca046d3b03853f0d077ad3ad130db886
- https://git.kernel.org/stable/c/7ae1345f6ad715acbcdc9e1ac28153684fd498bb
- https://git.kernel.org/stable/c/91f8f5342bee726ed5692583d58f69e7cc9ae60e
- https://git.kernel.org/stable/c/a3c148955c22fe1d94d7a2096005679c1f22eddf
- https://git.kernel.org/stable/c/dfc0337c6dceb6449403b33ecb141f4a1458a1e9
- https://git.kernel.org/stable/c/ff2f5ec5d009844ec28f171123f9e58750cef4bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50352.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50352
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
