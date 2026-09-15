# [M] wifi: wilc1000: add missing unregister_netdev() in wilc_netdev_ifc_init()

## Summary
Severity: Medium
Advisory: CVE-2022-50361
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50361
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: add missing unregister_netdev() in wilc_netdev_ifc_init()

Fault injection test reports this issue:

kernel BUG at net/core/dev.c:10731!
invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI
Call Trace:
  <TASK>
  wilc_netdev_ifc_init+0x19f/0x220 [wilc1000 884bf126e9e98af6a708f266a8dffd53f99e4bf5]
  wilc_cfg80211_init+0x30c/0x380 [wilc1000 884bf126e9e98af6a708f266a8dffd53f99e4bf5]
  wilc_bus_probe+0xad/0x2b0 [wilc1000_spi 1520a7539b6589cc6cde2ae826a523a33f8bacff]
  spi_probe+0xe4/0x140
  really_probe+0x17e/0x3f0
  __driver_probe_device+0xe3/0x170
  driver_probe_device+0x49/0x120

The root case here is alloc_ordered_workqueue() fails, but
cfg80211_unregister_netdevice() or unregister_netdev() not be called in
error handling path. To fix add unregister_netdev goto lable to add the
unregister operation in error handling path.

## References
- https://git.kernel.org/stable/c/2b88974ecb358990e1c33fabcd0b9e142bab7f21
- https://git.kernel.org/stable/c/6da6ce086221803ed6c3b1db11096cecd3e58ec8
- https://git.kernel.org/stable/c/a1bdecedc7ad0512365267cd1a26bfc2ae455c59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50361.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50361
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
