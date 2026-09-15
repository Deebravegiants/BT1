# [H] pinctrl: devicetree: don't free uninitialized dev_name on error path

## Summary
Severity: High
Advisory: CVE-2026-74519
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74519
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: devicetree: don't free uninitialized dev_name on error path

dt_remember_or_free_map() duplicates dev_name for each map entry. If
kstrdup_const() fails, dt_free_map() frees dev_name in all num_maps
entries, including entries that have not been initialized.

Some pinctrl drivers, including pinctrl-imx, allocate the map with
kmalloc() and leave dev_name for the core to initialize. The untouched
entries therefore contain uninitialized data which is passed to
kfree_const().

Reproduced on qemu's mcimx6ul-evk (pinctrl-imx) with failslab injection
while binding the pinctrl-consuming device, under KASAN:

  BUG: KASAN: double-free in dt_free_map+0x34/0xa4
  Free of addr c425a900 by task init/1
   kfree from dt_free_map+0x34/0xa4
   dt_free_map from dt_remember_or_free_map+0x184/0x198
   dt_remember_or_free_map from pinctrl_dt_to_map+0x33c/0x4c8
   pinctrl_dt_to_map from create_pinctrl+0x9c/0x5c0

Initialize all dev_name fields to NULL before duplicating the device
name, making the full-map cleanup safe after a partial failure.

## References
- https://git.kernel.org/stable/c/015b5bcbcb622b32317642be91a7f79aa5413649
- https://git.kernel.org/stable/c/1586423da2739a80871ef6240016fcb9c7339bfb
- https://git.kernel.org/stable/c/321fe3584a8298386938130d138191aa35040b75
- https://git.kernel.org/stable/c/929f6396baade89999ec8a1281232c101cbc727d
- https://git.kernel.org/stable/c/9d00a5ac7cd3d32ae61140f4b8a62f136de84e7d
- https://git.kernel.org/stable/c/ad0ad3c228b6f76fde10f32047e0ec5fbc109dc8
- https://git.kernel.org/stable/c/dec5f0a8080502908dec5e35597c7ae07d533a3b
- https://git.kernel.org/stable/c/e3cfb22bad363bebcfd55d909e12d499cb8c5490
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74519.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74519
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
