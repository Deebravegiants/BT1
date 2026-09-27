# [H] net: drv: netdevsim: don't napi_complete() from netpoll

## Summary
Severity: High
Advisory: CVE-2025-38270
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38270
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: drv: netdevsim: don't napi_complete() from netpoll

netdevsim supports netpoll. Make sure we don't call napi_complete()
from it, since it may not be scheduled. Breno reports hitting a
warning in napi_complete_done():

WARNING: CPU: 14 PID: 104 at net/core/dev.c:6592 napi_complete_done+0x2cc/0x560
  __napi_poll+0x2d8/0x3a0
  handle_softirqs+0x1fe/0x710

This is presumably after netpoll stole the SCHED bit prematurely.

## References
- https://git.kernel.org/stable/c/1264971017b4d7141352a7fe29021bdfce5d885d
- https://git.kernel.org/stable/c/6837dd877270c57689bd866de9f3de14172c2439
- https://git.kernel.org/stable/c/a8ff2e362d901200a1075c3ca9c56d9c7bbef389
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38270.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
