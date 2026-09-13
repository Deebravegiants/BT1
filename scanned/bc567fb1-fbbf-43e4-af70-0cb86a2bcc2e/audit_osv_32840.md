# [H] net_sched: red: fix a race in __red_change()

## Summary
Severity: High
Advisory: CVE-2025-38108
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38108
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: red: fix a race in __red_change()

Gerrard Tai reported a race condition in RED, whenever SFQ perturb timer
fires at the wrong time.

The race is as follows:

CPU 0                                 CPU 1
[1]: lock root
[2]: qdisc_tree_flush_backlog()
[3]: unlock root
 |
 |                                    [5]: lock root
 |                                    [6]: rehash
 |                                    [7]: qdisc_tree_reduce_backlog()
 |
[4]: qdisc_put()

This can be abused to underflow a parent's qlen.

Calling qdisc_purge_queue() instead of qdisc_tree_flush_backlog()
should fix the race, because all packets will be purged from the qdisc
before releasing the lock.

## References
- https://git.kernel.org/stable/c/110a47efcf23438ff8d31dbd9c854fae2a48bf98
- https://git.kernel.org/stable/c/2790c4ec481be45a80948d059cd7c9a06bc37493
- https://git.kernel.org/stable/c/2a71924ca4af59ffc00f0444732b6cd54b153d0e
- https://git.kernel.org/stable/c/444ad445df5496a785705019268a8a84b84484bb
- https://git.kernel.org/stable/c/4b755305b2b0618e857fdadb499365b5f2e478d1
- https://git.kernel.org/stable/c/85a3e0ede38450ea3053b8c45d28cf55208409b8
- https://git.kernel.org/stable/c/a1bf6a4e9264a685b0e642994031f9c5aad72414
- https://git.kernel.org/stable/c/f569984417a4e12c67366e69bdcb752970de921d
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38108.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
