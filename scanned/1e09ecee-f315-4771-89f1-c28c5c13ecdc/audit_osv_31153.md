# [M] clk: mmp2: call pm_genpd_init() only after genpd.name is set

## Summary
Severity: Medium
Advisory: CVE-2024-58081
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58081
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mmp2: call pm_genpd_init() only after genpd.name is set

Setting the genpd's struct device's name with dev_set_name() is
happening within pm_genpd_init(). If it remains NULL, things can blow up
later, such as when crafting the devfs hierarchy for the power domain:

  Unable to handle kernel NULL pointer dereference at virtual address 00000000 when read
  ...
  Call trace:
   strlen from start_creating+0x90/0x138
   start_creating from debugfs_create_dir+0x20/0x178
   debugfs_create_dir from genpd_debug_add.part.0+0x4c/0x144
   genpd_debug_add.part.0 from genpd_debug_init+0x74/0x90
   genpd_debug_init from do_one_initcall+0x5c/0x244
   do_one_initcall from kernel_init_freeable+0x19c/0x1f4
   kernel_init_freeable from kernel_init+0x1c/0x12c
   kernel_init from ret_from_fork+0x14/0x28

Bisecting tracks this crash back to commit 899f44531fe6 ("pmdomain: core:
Add GENPD_FLAG_DEV_NAME_FW flag"), which exchanges use of genpd->name
with dev_name(&genpd->dev) in genpd_debug_add.part().

## References
- https://git.kernel.org/stable/c/763517124e27b07fa300b486d7d13c5d563a215e
- https://git.kernel.org/stable/c/e24b15d4704dcb73920c3d18a6157abd18df08c1
- https://git.kernel.org/stable/c/eca01d5911fb34218d10a58d8d9534b758c8fd0a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58081.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
