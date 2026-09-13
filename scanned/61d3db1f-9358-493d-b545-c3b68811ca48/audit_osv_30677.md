# [M] netfilter: IDLETIMER: Fix for possible ABBA deadlock

## Summary
Severity: Medium
Advisory: CVE-2024-54683
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-54683
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: IDLETIMER: Fix for possible ABBA deadlock

Deletion of the last rule referencing a given idletimer may happen at
the same time as a read of its file in sysfs:

| ======================================================
| WARNING: possible circular locking dependency detected
| 6.12.0-rc7-01692-g5e9a28f41134-dirty #594 Not tainted
| ------------------------------------------------------
| iptables/3303 is trying to acquire lock:
| ffff8881057e04b8 (kn->active#48){++++}-{0:0}, at: __kernfs_remove+0x20
|
| but task is already holding lock:
| ffffffffa0249068 (list_mutex){+.+.}-{3:3}, at: idletimer_tg_destroy_v]
|
| which lock already depends on the new lock.

A simple reproducer is:

| #!/bin/bash
|
| while true; do
|         iptables -A INPUT -i foo -j IDLETIMER --timeout 10 --label "testme"
|         iptables -D INPUT -i foo -j IDLETIMER --timeout 10 --label "testme"
| done &
| while true; do
|         cat /sys/class/xt_idletimer/timers/testme >/dev/null
| done

Avoid this by freeing list_mutex right after deleting the element from
the list, then continuing with the teardown.

## References
- https://git.kernel.org/stable/c/45fe76573a2557f632e248cc141342233f422b9a
- https://git.kernel.org/stable/c/8c2c8445cda8f59c38dec7dc10509bcb23ae26a0
- https://git.kernel.org/stable/c/f36b01994d68ffc253c8296e2228dfe6e6431c03
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54683.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-54683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
