# [H] net_sched: prio: fix a race in prio_tune()

## Summary
Severity: High
Advisory: CVE-2025-38083
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-20
Source: https://osv.dev/vulnerability/CVE-2025-38083
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: prio: fix a race in prio_tune()

Gerrard Tai reported a race condition in PRIO, whenever SFQ perturb timer
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
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/20f68e6a9e41693cb0e55e5b9ebbcb40983a4b8f
- https://git.kernel.org/stable/c/3aaa7c01cf19d9b9bb64b88b65c3a6fd05da2eb4
- https://git.kernel.org/stable/c/4483d8b9127591c60c4eb789d6cab953bc4522a9
- https://git.kernel.org/stable/c/46c15c9d0f65c9ba857d63f53264f4b17e8a715f
- https://git.kernel.org/stable/c/53d11560e957d53ee87a0653d258038ce12361b7
- https://git.kernel.org/stable/c/93f9eeb678d4c9c1abf720b3615fa8299a490845
- https://git.kernel.org/stable/c/d35acc1be3480505b5931f17e4ea9b7617fea4d3
- https://git.kernel.org/stable/c/e3f6745006dc9423d2b065b90f191cfa11b1b584
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38083.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
