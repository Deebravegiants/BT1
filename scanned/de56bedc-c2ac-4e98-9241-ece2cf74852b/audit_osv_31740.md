# [H] netem: Update sch->q.qlen before qdisc_tree_reduce_backlog()

## Summary
Severity: High
Advisory: CVE-2025-21703
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-21703
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netem: Update sch->q.qlen before qdisc_tree_reduce_backlog()

qdisc_tree_reduce_backlog() notifies parent qdisc only if child
qdisc becomes empty, therefore we need to reduce the backlog of the
child qdisc before calling it. Otherwise it would miss the opportunity
to call cops->qlen_notify(), in the case of DRR, it resulted in UAF
since DRR uses ->qlen_notify() to maintain its active list.

## References
- https://git.kernel.org/stable/c/1f8e3f4a4b8b90ad274dfbc66fc7d55cb582f4d5
- https://git.kernel.org/stable/c/6312555249082d6d8cc5321ff725df05482d8b83
- https://git.kernel.org/stable/c/638ba5089324796c2ee49af10427459c2de35f71
- https://git.kernel.org/stable/c/7b79ca9a1de6a428d486ff52fb3d602321c08f55
- https://git.kernel.org/stable/c/7f31d74fcc556a9166b1bb20515542de7bb939d1
- https://git.kernel.org/stable/c/839ecc583fa00fab785fde1c85a326743657fd32
- https://git.kernel.org/stable/c/98a2c685293aae122f688cde11d9334dddc5d207
- https://git.kernel.org/stable/c/e395fec75ac2dbffc99b4bce57b7f1f3c5449f2c
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21703.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21703
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
