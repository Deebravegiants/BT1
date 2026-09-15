# [H] net_sched: sch_sfq: fix a potential crash on gso_skb handling

## Summary
Severity: High
Advisory: CVE-2025-38115
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38115
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: sch_sfq: fix a potential crash on gso_skb handling

SFQ has an assumption of always being able to queue at least one packet.

However, after the blamed commit, sch->q.len can be inflated by packets
in sch->gso_skb, and an enqueue() on an empty SFQ qdisc can be followed
by an immediate drop.

Fix sfq_drop() to properly clear q->tail in this situation.


ip netns add lb
ip link add dev to-lb type veth peer name in-lb netns lb
ethtool -K to-lb tso off                 # force qdisc to requeue gso_skb
ip netns exec lb ethtool -K in-lb gro on # enable NAPI
ip link set dev to-lb up
ip -netns lb link set dev in-lb up
ip addr add dev to-lb 192.168.20.1/24
ip -netns lb addr add dev in-lb 192.168.20.2/24
tc qdisc replace dev to-lb root sfq limit 100

ip netns exec lb netserver

netperf -H 192.168.20.2 -l 100 &
netperf -H 192.168.20.2 -l 100 &
netperf -H 192.168.20.2 -l 100 &
netperf -H 192.168.20.2 -l 100 &

## References
- https://git.kernel.org/stable/c/5814a7fc3abb41f63f2d44c9d3ff9d4e62965b72
- https://git.kernel.org/stable/c/82448d4dcd8406dec688632a405fdcf7f170ec69
- https://git.kernel.org/stable/c/82ffbe7776d0ac084031f114167712269bf3d832
- https://git.kernel.org/stable/c/9c19498bdd7cb9d854bd3c54260f71cf7408495e
- https://git.kernel.org/stable/c/b44f791f27b14c9eb6b907fbe51f2ba8bec32085
- https://git.kernel.org/stable/c/b4e9bab6011b9559b7c157b16b91ae46d4d8c533
- https://git.kernel.org/stable/c/c337efb20d6d9f9bbb4746f6b119917af5c886dc
- https://git.kernel.org/stable/c/d1bc80da75c789f2f6830df89d91fb2f7a509943
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38115.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
