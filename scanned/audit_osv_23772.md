# [M] thermal/core: Fix memory leak in __thermal_cooling_device_register()

## Summary
Severity: Medium
Advisory: CVE-2022-49468
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49468
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal/core: Fix memory leak in __thermal_cooling_device_register()

I got memory leak as follows when doing fault injection test:

unreferenced object 0xffff888010080000 (size 264312):
  comm "182", pid 102533, jiffies 4296434960 (age 10.100s)
  hex dump (first 32 bytes):
    00 00 00 00 ad 4e ad de ff ff ff ff 00 00 00 00  .....N..........
    ff ff ff ff ff ff ff ff 40 7f 1f b9 ff ff ff ff  ........@.......
  backtrace:
    [<0000000038b2f4fc>] kmalloc_order_trace+0x1d/0x110 mm/slab_common.c:969
    [<00000000ebcb8da5>] __kmalloc+0x373/0x420 include/linux/slab.h:510
    [<0000000084137f13>] thermal_cooling_device_setup_sysfs+0x15d/0x2d0 include/linux/slab.h:586
    [<00000000352b8755>] __thermal_cooling_device_register+0x332/0xa60 drivers/thermal/thermal_core.c:927
    [<00000000fb9f331b>] devm_thermal_of_cooling_device_register+0x6b/0xf0 drivers/thermal/thermal_core.c:1041
    [<000000009b8012d2>] max6650_probe.cold+0x557/0x6aa drivers/hwmon/max6650.c:211
    [<00000000da0b7e04>] i2c_device_probe+0x472/0xac0 drivers/i2c/i2c-core-base.c:561

If device_register() fails, thermal_cooling_device_destroy_sysfs() need be called
to free the memory allocated in thermal_cooling_device_setup_sysfs().

## References
- https://git.kernel.org/stable/c/18530bedd221160823f63ccc20dd55c7a03edbcf
- https://git.kernel.org/stable/c/21ccc58b671aea924f2481cf5c1cf0ebbfd3552d
- https://git.kernel.org/stable/c/3802171f0b5b8b831f4ade5c827547cb323a5bb2
- https://git.kernel.org/stable/c/98a160e898c0f4a979af9de3ab48b4b1d42d1dbb
- https://git.kernel.org/stable/c/9abdf0c0184230f0cb5c6685aabf33dda89aa9fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49468.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49468
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
