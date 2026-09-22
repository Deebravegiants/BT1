# [H] octeontx2-pf: QOS: Refactor TC_HTB_LEAF_DEL_LAST callback

## Summary
Severity: High
Advisory: CVE-2025-38278
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38278
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: QOS: Refactor TC_HTB_LEAF_DEL_LAST callback

This patch addresses below issues,

1. Active traffic on the leaf node must be stopped before its send queue
   is reassigned to the parent. This patch resolves the issue by marking
   the node as 'Inner'.

2. During a system reboot, the interface receives TC_HTB_LEAF_DEL
   and TC_HTB_LEAF_DEL_LAST callbacks to delete its HTB queues.
   In the case of TC_HTB_LEAF_DEL_LAST, although the same send queue
   is reassigned to the parent, the current logic still attempts to update
   the real number of queues, leadning to below warnings

        New queues can't be registered after device unregistration.
        WARNING: CPU: 0 PID: 6475 at net/core/net-sysfs.c:1714
        netdev_queue_update_kobjects+0x1e4/0x200

## References
- https://git.kernel.org/stable/c/5df8db01d6a4e9c35a5ba5d7e130d5cecd3ffcb4
- https://git.kernel.org/stable/c/67af4ec948e8ce3ea53a9cf614d01fddf172e56d
- https://git.kernel.org/stable/c/ec62c99914a79d84c8de5ba1b94d62f2ed721f2a
- https://git.kernel.org/stable/c/f1fca0eae5a0573f226f46c6871260278e7dda12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38278.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38278
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
