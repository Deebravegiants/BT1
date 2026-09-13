# [H] media: pci: cx23885: Fix the error handling in cx23885_initdev()

## Summary
Severity: High
Advisory: CVE-2022-49524
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49524
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: pci: cx23885: Fix the error handling in cx23885_initdev()

When the driver fails to call the dma_set_mask(), the driver will get
the following splat:

[   55.853884] BUG: KASAN: use-after-free in __process_removed_driver+0x3c/0x240
[   55.854486] Read of size 8 at addr ffff88810de60408 by task modprobe/590
[   55.856822] Call Trace:
[   55.860327]  __process_removed_driver+0x3c/0x240
[   55.861347]  bus_for_each_dev+0x102/0x160
[   55.861681]  i2c_del_driver+0x2f/0x50

This is because the driver has initialized the i2c related resources
in cx23885_dev_setup() but not released them in error handling, fix this
bug by modifying the error path that jumps after failing to call the
dma_set_mask().

## References
- https://git.kernel.org/stable/c/453514a874c78df1e7804e6e3aaa60c8d8deb6a8
- https://git.kernel.org/stable/c/6041d1a0365baa729b6adfb6ed5386d9388018db
- https://git.kernel.org/stable/c/7b9978e1c94e569d65a0e7e719abb9340f5db4a0
- https://git.kernel.org/stable/c/86bd6a579c6c60547706cabf299cd2c9feab3332
- https://git.kernel.org/stable/c/98106f100f50c487469903b9cf6d966785fc9cc3
- https://git.kernel.org/stable/c/ca17e7a532d1a55466cc007b3f4d319541a27493
- https://git.kernel.org/stable/c/e8123311cf06d7dae71e8c5fe78e0510d20cd30b
- https://git.kernel.org/stable/c/fa636e9ee4442215cd9a2e079cd5a8e1fe0cb8ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49524.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49524
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
