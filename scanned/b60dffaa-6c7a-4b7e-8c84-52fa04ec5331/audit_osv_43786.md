# [H] gpio: pca953x: fix pca953x_irq_bus_sync_unlock regmap lock

## Summary
Severity: High
Advisory: CVE-2026-74733
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74733
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: pca953x: fix pca953x_irq_bus_sync_unlock regmap lock

Locking is disabled in the regmap config as this driver uses its own
lock. This means that all calls to regmap functions (read or write) must
hold the i2c_lock. The function pca953x_irq_bus_sync_unlock() did not do
this, and it was therefore possible that multiple threads could cause an
incorrect register to be read/written.

A previous patch partly fixed this, but only protected the write to the
interrupt mask register, and not the read from the direction register.

## References
- https://git.kernel.org/stable/c/9dc325327babe7f159e84cbe9380a45342da0585
- https://git.kernel.org/stable/c/e6a2f5f845f50b0c4299bace5111f56d3390a090
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74733.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74733
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
