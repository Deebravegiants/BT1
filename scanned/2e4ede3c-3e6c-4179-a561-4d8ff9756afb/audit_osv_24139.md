# [M] media: vimc: Fix wrong function called when vimc_init() fails

## Summary
Severity: Medium
Advisory: CVE-2022-50340
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50340
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vimc: Fix wrong function called when vimc_init() fails

In vimc_init(), when platform_driver_register(&vimc_pdrv) fails,
platform_driver_unregister(&vimc_pdrv) is wrongly called rather than
platform_device_unregister(&vimc_pdev), which causes kernel warning:

 Unexpected driver unregister!
 WARNING: CPU: 1 PID: 14517 at drivers/base/driver.c:270 driver_unregister+0x8f/0xb0
 RIP: 0010:driver_unregister+0x8f/0xb0
 Call Trace:
  <TASK>
  vimc_init+0x7d/0x1000 [vimc]
  do_one_initcall+0xd0/0x4e0
  do_init_module+0x1cf/0x6b0
  load_module+0x65c2/0x7820

## References
- https://git.kernel.org/stable/c/14d85b600bb1f6f8ef61fa8fc1907e2e623d8350
- https://git.kernel.org/stable/c/681ac2902039d9b497b3ae18fdc204314979e61e
- https://git.kernel.org/stable/c/9c9ff35d68691aaea85b2e93763772e23930b3a3
- https://git.kernel.org/stable/c/f38df8984ef1b45ba23888d0e232cc21a95bd04b
- https://git.kernel.org/stable/c/f74d3f326d1d5b8951ce263c59a121ecfa65e7c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50340.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
