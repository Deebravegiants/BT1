# [H] mfd: cros_ec: Delay dev_set_drvdata() until probe success

## Summary
Severity: High
Advisory: CVE-2026-64420
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64420
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mfd: cros_ec: Delay dev_set_drvdata() until probe success

If ec_device_probe() fails, cros_ec_class_release releases memory for the
cros_ec_dev structure. However, because the drvdata was already set,
sub-drivers like cros_ec_typec can still retrieve the stale pointer via the
platform device. This leads to a use-after-free when cros_ec_typec attempts
to access &typec->ec->ec->dev on a device that has already been released.
Move dev_set_drvdata() to ensure that the pointer is only made available
once all initialization steps have succeeded.

 sysfs: cannot create duplicate filename '/class/chromeos/cros_ec'
 Call trace:
  sysfs_do_create_link_sd+0x94/0xdc
  sysfs_create_link+0x30/0x44
  device_add_class_symlinks+0x90/0x13c
  device_add+0xf0/0x50c
  ec_device_probe+0x150/0x4f0
  platform_probe+0xa0/0xe0
 ...
 BUG: KASAN: invalid-access in __memcpy+0x44/0x230
 Write at addr f5ffff809e2d33ac by task kworker/u32:5/125
 Pointer tag: [f5], memory tag: [fe]
 Tainted : [W]=WARN, [O]=OOT_MODULE
 Hardware name: Google Navi unprovisioned 0x7FFFFFFF/sku0 board/sku3
 Workqueue: events_unbound deferred_probe_work_func
 Call trace:
  __memcpy+0x44/0x230
  cros_ec_check_features+0x60/0xcc [cros_ec_proto]
  cros_typec_probe+0xe8/0x6e0 [cros_ec_typec]
  platform_probe+0xa0/0xe0

## References
- https://git.kernel.org/stable/c/24522713034d521ea4b5f5f36342e2b2f7e73bd6
- https://git.kernel.org/stable/c/257203d83204b192d1265a916b42ca0d499bb117
- https://git.kernel.org/stable/c/729ae27dc2503a7c1f92da1859efb45da03e4fa0
- https://git.kernel.org/stable/c/8b2c1d41bc36c100b38ce5ee6def246c527eaf8a
- https://git.kernel.org/stable/c/b5f41d5bf08e7b1b14fa0bd640975e6d78dc006d
- https://git.kernel.org/stable/c/ed2941e5db016a0c600b25f1972620e6e223d9fa
- https://git.kernel.org/stable/c/f7e81dc181d9fe8ab977158042cd193e8cc12091
- https://git.kernel.org/stable/c/fc030c5b116f668d4ca86dca63742ddbc98d1665
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64420.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64420
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
