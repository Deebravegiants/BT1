# [M] net/sched: netem: account for backlog updates from child qdisc

## Summary
Severity: Medium
Advisory: CVE-2024-56770
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-56770
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.4.288, >=5.5.0 <5.10.232, >=5.11.0 <5.15.175, >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: netem: account for backlog updates from child qdisc

In general, 'qlen' of any classful qdisc should keep track of the
number of packets that the qdisc itself and all of its children holds.
In case of netem, 'qlen' only accounts for the packets in its internal
tfifo. When netem is used with a child qdisc, the child qdisc can use
'qdisc_tree_reduce_backlog' to inform its parent, netem, about created
or dropped SKBs. This function updates 'qlen' and the backlog statistics
of netem, but netem does not account for changes made by a child qdisc.
'qlen' then indicates the wrong number of packets in the tfifo.
If a child qdisc creates new SKBs during enqueue and informs its parent
about this, netem's 'qlen' value is increased. When netem dequeues the
newly created SKBs from the child, the 'qlen' in netem is not updated.
If 'qlen' reaches the configured sch->limit, the enqueue function stops
working, even though the tfifo is not full.

Reproduce the bug:
Ensure that the sender machine has GSO enabled. Configure netem as root
qdisc and tbf as its child on the outgoing interface of the machine
as follows:
$ tc qdisc add dev <oif> root handle 1: netem delay 100ms limit 100
$ tc qdisc add dev <oif> parent 1:0 tbf rate 50Mbit burst 1542 latency 50ms

Send bulk TCP traffic out via this interface, e.g., by running an iPerf3
client on the machine. Check the qdisc statistics:
$ tc -s qdisc show dev <oif>

Statistics after 10s of iPerf3 TCP test before the fix (note that
netem's backlog > limit, netem stopped accepting packets):
qdisc netem 1: root refcnt 2 limit 1000 delay 100ms
 Sent 2767766 bytes 1848 pkt (dropped 652, overlimits 0 requeues 0)
 backlog 4294528236b 1155p requeues 0
qdisc tbf 10: parent 1:1 rate 50Mbit burst 1537b lat 50ms
 Sent 2767766 bytes 1848 pkt (dropped 327, overlimits 7601 requeues 0)
 backlog 0b 0p requeues 0

Statistics after the fix:
qdisc netem 1: root refcnt 2 limit 1000 delay 100ms
 Sent 37766372 bytes 24974 pkt (dropped 9, overlimits 0 requeues 0)
 backlog 0b 0p requeues 0
qdisc tbf 10: parent 1:1 rate 50Mbit burst 1537b lat 50ms
 Sent 37766372 bytes 24974 pkt (dropped 327, overlimits 96017 requeues 0)
 backlog 0b 0p requeues 0

tbf segments the GSO SKBs (tbf_segment) and updates the netem's 'qlen'.
The interface fully stops transferring packets and "locks". In this case,
the child qdisc and tfifo are empty, but 'qlen' indicates the tfifo is at
its limit and no more packets are accepted.

This patch adds a counter for the entries in the tfifo. Netem's 'qlen' is
only decreased when a packet is returned by its dequeue function, and not
during enqueuing into the child qdisc. External updates to 'qlen' are thus
accounted for and only the behavior of the backlog statistics changes. As
in other qdiscs, 'qlen' then keeps track of  how many packets are held in
netem and all of its children. As before, sch->limit remains as the
maximum number of packets in the tfifo. The same applies to netem's
backlog statistics.

## References
- https://git.kernel.org/stable/c/10df49cfca73dfbbdb6c4150d859f7e8926ae427
- https://git.kernel.org/stable/c/216509dda290f6db92c816dd54b83c1df9da9e76
- https://git.kernel.org/stable/c/356078a5c55ec8d2061fcc009fb8599f5b0527f9
- https://git.kernel.org/stable/c/3824c5fad18eeb7abe0c4fc966f29959552dca3e
- https://git.kernel.org/stable/c/83c6ab12f08dcc09d4c5ac86fdb89736b28f1d31
- https://git.kernel.org/stable/c/c2047b0e216c8edce227d7c42f99ac2877dad0e4
- https://git.kernel.org/stable/c/f8d4bc455047cf3903cd6f85f49978987dbb3027
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56770.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56770
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
