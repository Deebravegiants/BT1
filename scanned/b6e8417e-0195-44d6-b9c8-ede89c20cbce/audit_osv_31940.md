# [M] ARM: dts: bcm2711: Fix xHCI power-domain

## Summary
Severity: Medium
Advisory: CVE-2025-22011
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-22011
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: dts: bcm2711: Fix xHCI power-domain

During s2idle tests on the Raspberry CM4 the VPU firmware always crashes
on xHCI power-domain resume:

root@raspberrypi:/sys/power# echo freeze > state
[   70.724347] xhci_suspend finished
[   70.727730] xhci_plat_suspend finished
[   70.755624] bcm2835-power bcm2835-power: Power grafx off
[   70.761127]  USB: Set power to 0

[   74.653040]  USB: Failed to set power to 1 (-110)

This seems to be caused because of the mixed usage of
raspberrypi-power and bcm2835-power at the same time. So avoid
the usage of the VPU firmware power-domain driver, which
prevents the VPU crash.

## References
- https://git.kernel.org/stable/c/393947e06867923d4c2be380d46efd03407a8ce2
- https://git.kernel.org/stable/c/b8a47aa0b3df701d0fc41b3caf78d00571776be0
- https://git.kernel.org/stable/c/f44fa354a0715577ca32b085f6f60bcf32c748dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22011.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
