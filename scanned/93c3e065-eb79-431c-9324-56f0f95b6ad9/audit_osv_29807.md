# [H] sch/netem: fix use after free in netem_dequeue

## Summary
Severity: High
Advisory: CVE-2024-46800
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46800
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sch/netem: fix use after free in netem_dequeue

If netem_dequeue() enqueues packet to inner qdisc and that qdisc
returns __NET_XMIT_STOLEN. The packet is dropped but
qdisc_tree_reduce_backlog() is not called to update the parent's
q.qlen, leading to the similar use-after-free as Commit
e04991a48dbaf382 ("netem: fix return value if duplicate enqueue
fails")

Commands to trigger KASAN UaF:

ip link add type dummy
ip link set lo up
ip link set dummy0 up
tc qdisc add dev lo parent root handle 1: drr
tc filter add dev lo parent 1: basic classid 1:1
tc class add dev lo classid 1:1 drr
tc qdisc add dev lo parent 1:1 handle 2: netem
tc qdisc add dev lo parent 2: handle 3: drr
tc filter add dev lo parent 3: basic classid 3:1 action mirred egress
redirect dev dummy0
tc class add dev lo classid 3:1 drr
ping -c1 -W0.01 localhost # Trigger bug
tc class del dev lo classid 1:1
tc class add dev lo classid 1:1 drr
ping -c1 -W0.01 localhost # UaF

## References
- https://git.kernel.org/stable/c/14f91ab8d391f249b845916820a56f42cf747241
- https://git.kernel.org/stable/c/295ad5afd9efc5f67b86c64fce28fb94e26dc4c9
- https://git.kernel.org/stable/c/32008ab989ddcff1a485fa2b4906234c25dc5cd6
- https://git.kernel.org/stable/c/3b3a2a9c6349e25a025d2330f479bc33a6ccb54a
- https://git.kernel.org/stable/c/98c75d76187944296068d685dfd8a1e9fd8c4fdc
- https://git.kernel.org/stable/c/db2c235682913a63054e741fe4e19645fdf2d68e
- https://git.kernel.org/stable/c/dde33a9d0b80aae0c69594d1f462515d7ff1cb3d
- https://git.kernel.org/stable/c/f0bddb4de043399f16d1969dad5ee5b984a64e7b
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46800.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46800
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
