# [H] batman-adv: fix tp_meter counter underflow during shutdown

## Summary
Severity: High
Advisory: CVE-2026-52919
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52919
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: fix tp_meter counter underflow during shutdown

batadv_tp_sender_shutdown() unconditionally decrements the "sending"
atomic counter. If multiple paths (e.g. timeout, user cancel, and
normal finish) call this function, the counter can underflow to -1.

Since the sender logic treats any non-zero value as "still sending",
a negative value causes the sender kthread to loop indefinitely.
This leads to a use-after-free when the interface is removed while
the zombie thread is still active.

Fix this by using atomic_xchg() to ensure the counter only transitions
from 1 to 0 once.

[sven: added missing change in batadv_tp_send]

## References
- https://git.kernel.org/stable/c/01cefc5923889e29dbb5f281c3d457714ceb9c00
- https://git.kernel.org/stable/c/90ae3eae06b7b8ab9f6250b9497c860915b4c17b
- https://git.kernel.org/stable/c/94f3b133168d1c49895e7cc6afbcf1cc0b354602
- https://git.kernel.org/stable/c/abae88fa254f2981d39ac003a7b302528a22af64
- https://git.kernel.org/stable/c/aeae11c5dad9cd0d50723890bdd866f8e6db2e7d
- https://git.kernel.org/stable/c/c1bac194733aabd731aafa6a01350c229e187dba
- https://git.kernel.org/stable/c/c66d20a3ff095e3f000551d208ec2606616db15c
- https://git.kernel.org/stable/c/e75e2ab463b5b34df6b98f94d740aff327ce9f6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52919.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52919
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
