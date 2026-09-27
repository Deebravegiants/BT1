# [H] net: dev_ioctl: take ops lock in hwtstamp lower paths

## Summary
Severity: High
Advisory: CVE-2025-39908
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39908
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dev_ioctl: take ops lock in hwtstamp lower paths

ndo hwtstamp callbacks are expected to run under the per-device ops
lock. Make the lower get/set paths consistent with the rest of ndo
invocations.

Kernel log:
WARNING: CPU: 13 PID: 51364 at ./include/net/netdev_lock.h:70 __netdev_update_features+0x4bd/0xe60
...
RIP: 0010:__netdev_update_features+0x4bd/0xe60
...
Call Trace:
<TASK>
netdev_update_features+0x1f/0x60
mlx5_hwtstamp_set+0x181/0x290 [mlx5_core]
mlx5e_hwtstamp_set+0x19/0x30 [mlx5_core]
dev_set_hwtstamp_phylib+0x9f/0x220
dev_set_hwtstamp_phylib+0x9f/0x220
dev_set_hwtstamp+0x13d/0x240
dev_ioctl+0x12f/0x4b0
sock_ioctl+0x171/0x370
__x64_sys_ioctl+0x3f7/0x900
? __sys_setsockopt+0x69/0xb0
do_syscall_64+0x6f/0x2e0
entry_SYSCALL_64_after_hwframe+0x4b/0x53
...
</TASK>
....
---[ end trace 0000000000000000 ]---

Note that the mlx5_hwtstamp_set and mlx5e_hwtstamp_set functions shown
in the trace come from an in progress patch converting the legacy ioctl
to ndo_hwtstamp_get/set and are not present in mainline.

## References
- https://git.kernel.org/stable/c/2d92fa0cdc02291de57f72170e8b60cef0cf5372
- https://git.kernel.org/stable/c/686cab5a18e443e1d5f2abb17bed45837836425f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39908.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
