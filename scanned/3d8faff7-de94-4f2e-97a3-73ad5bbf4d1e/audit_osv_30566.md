# [H] net: sched: fix ordering of qlen adjustment

## Summary
Severity: High
Advisory: CVE-2024-53164
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53164
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: fix ordering of qlen adjustment

Changes to sch->q.qlen around qdisc_tree_reduce_backlog() need to happen
_before_ a call to said function because otherwise it may fail to notify
parent qdiscs when the child is about to become empty.

## References
- https://git.kernel.org/stable/c/33db36b3c53d0fda2699ea39ba72bee4de8336e8
- https://git.kernel.org/stable/c/44782565e1e6174c94bddfa72ac7267cd09c1648
- https://git.kernel.org/stable/c/489422e2befff88a1de52b2acebe7b333bded025
- https://git.kernel.org/stable/c/5e473f462a16f1a34e49ea4289a667d2e4f35b52
- https://git.kernel.org/stable/c/5eb7de8cd58e73851cd37ff8d0666517d9926948
- https://git.kernel.org/stable/c/97e13434b5da8e91bdf965352fad2141d13d72d3
- https://git.kernel.org/stable/c/e3e54ad9eff8bdaa70f897e5342e34b76109497f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53164.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53164
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
