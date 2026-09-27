# [M] regulator: da9121: Fix uninit-value in da9121_assign_chip_model()

## Summary
Severity: Medium
Advisory: CVE-2022-49507
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49507
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: da9121: Fix uninit-value in da9121_assign_chip_model()

KASAN report slab-out-of-bounds in __regmap_init as follows:

BUG: KASAN: slab-out-of-bounds in __regmap_init drivers/base/regmap/regmap.c:841
Read of size 1 at addr ffff88803678cdf1 by task xrun/9137

CPU: 0 PID: 9137 Comm: xrun Tainted: G        W         5.18.0-rc2
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1ubuntu1.1 04/01/2014
Call Trace:
 <TASK>
 dump_stack_lvl+0xe8/0x15a lib/dump_stack.c:88
 print_report.cold+0xcd/0x69b mm/kasan/report.c:313
 kasan_report+0x8e/0xc0 mm/kasan/report.c:491
 __regmap_init+0x4540/0x4ba0 drivers/base/regmap/regmap.c:841
 __devm_regmap_init+0x7a/0x100 drivers/base/regmap/regmap.c:1266
 __devm_regmap_init_i2c+0x65/0x80 drivers/base/regmap/regmap-i2c.c:394
 da9121_i2c_probe+0x386/0x6d1 drivers/regulator/da9121-regulator.c:1039
 i2c_device_probe+0x959/0xac0 drivers/i2c/i2c-core-base.c:563

This happend when da9121 device is probe by da9121_i2c_id, but with
invalid dts. Thus, chip->subvariant_id is set to -EINVAL, and later
da9121_assign_chip_model() will access 'regmap' without init it.

Fix it by return -EINVAL from da9121_assign_chip_model() if
'chip->subvariant_id' is invalid.

## References
- https://git.kernel.org/stable/c/60f21eda69f1b5727a97d2077da766eb27fcc21f
- https://git.kernel.org/stable/c/7da64c7c82c9b29b628a62c88a8c2fb06990563d
- https://git.kernel.org/stable/c/bab76514aca36bc513224525d5598da676938218
- https://git.kernel.org/stable/c/be96baa0c79588084e0d7a4fa21c574cec9a57f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49507.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49507
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
