# [M] net: sched: sfb: fix null pointer access issue when sfb_init() fails

## Summary
Severity: Medium
Advisory: CVE-2022-50356
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50356
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.152, >=5.11.0 <5.15.76, >=5.16.0 <6.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: sfb: fix null pointer access issue when sfb_init() fails

When the default qdisc is sfb, if the qdisc of dev_queue fails to be
inited during mqprio_init(), sfb_reset() is invoked to clear resources.
In this case, the q->qdisc is NULL, and it will cause gpf issue.

The process is as follows:
qdisc_create_dflt()
	sfb_init()
		tcf_block_get()          --->failed, q->qdisc is NULL
	...
	qdisc_put()
		...
		sfb_reset()
			qdisc_reset(q->qdisc)    --->q->qdisc is NULL
				ops = qdisc->ops

The following is the Call Trace information:
general protection fault, probably for non-canonical address
0xdffffc0000000003: 0000 [#1] PREEMPT SMP KASAN
KASAN: null-ptr-deref in range [0x0000000000000018-0x000000000000001f]
RIP: 0010:qdisc_reset+0x2b/0x6f0
Call Trace:
<TASK>
sfb_reset+0x37/0xd0
qdisc_reset+0xed/0x6f0
qdisc_destroy+0x82/0x4c0
qdisc_put+0x9e/0xb0
qdisc_create_dflt+0x2c3/0x4a0
mqprio_init+0xa71/0x1760
qdisc_create+0x3eb/0x1000
tc_modify_qdisc+0x408/0x1720
rtnetlink_rcv_msg+0x38e/0xac0
netlink_rcv_skb+0x12d/0x3a0
netlink_unicast+0x4a2/0x740
netlink_sendmsg+0x826/0xcc0
sock_sendmsg+0xc5/0x100
____sys_sendmsg+0x583/0x690
___sys_sendmsg+0xe8/0x160
__sys_sendmsg+0xbf/0x160
do_syscall_64+0x35/0x80
entry_SYSCALL_64_after_hwframe+0x46/0xb0
RIP: 0033:0x7f2164122d04
</TASK>

## References
- https://git.kernel.org/stable/c/2a3fc78210b9f0e85372a2435368962009f480fc
- https://git.kernel.org/stable/c/723399af2795fb95687a531c9480464b5f489333
- https://git.kernel.org/stable/c/c2e1e59d59fafe297779ceae1fe0e6fbebc3e745
- https://git.kernel.org/stable/c/ded86c4191a3c17f8200d17a7d8a6f63b74554ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50356.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
