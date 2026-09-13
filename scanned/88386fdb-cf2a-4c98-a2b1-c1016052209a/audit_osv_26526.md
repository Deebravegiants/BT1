# [M] power: supply: axp288_fuel_gauge: Fix external_power_changed race

## Summary
Severity: Medium
Advisory: CVE-2023-53310
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53310
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.31, >=6.2.0 <6.3.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

power: supply: axp288_fuel_gauge: Fix external_power_changed race

fuel_gauge_external_power_changed() dereferences info->bat,
which gets sets in axp288_fuel_gauge_probe() like this:

  info->bat = devm_power_supply_register(dev, &fuel_gauge_desc, &psy_cfg);

As soon as devm_power_supply_register() has called device_add()
the external_power_changed callback can get called. So there is a window
where fuel_gauge_external_power_changed() may get called while
info->bat has not been set yet leading to a NULL pointer dereference.

Fixing this is easy. The external_power_changed callback gets passed
the power_supply which will eventually get stored in info->bat,
so fuel_gauge_external_power_changed() can simply directly use
the passed in psy argument which is always valid.

## References
- https://git.kernel.org/stable/c/0456b912121e45b3ef54abe3135e5dcb541f956c
- https://git.kernel.org/stable/c/a636c6ba9ce898207f283271cb28511206ab739b
- https://git.kernel.org/stable/c/f8319774d6f1567d6e7d03653174ab0c82c5c66d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53310.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53310
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
