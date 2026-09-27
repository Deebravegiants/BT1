# [H] netfilter: conntrack: fix wrong ct->timeout value

## Summary
Severity: High
Advisory: CVE-2023-53635
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53635
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: fix wrong ct->timeout value

(struct nf_conn)->timeout is an interval before the conntrack
confirmed.  After confirmed, it becomes a timestamp.

It is observed that timeout of an unconfirmed conntrack:
- Set by calling ctnetlink_change_timeout(). As a result,
  `nfct_time_stamp` was wrongly added to `ct->timeout` twice.
- Get by calling ctnetlink_dump_timeout(). As a result,
  `nfct_time_stamp` was wrongly subtracted.

Call Trace:
 <TASK>
 dump_stack_lvl
 ctnetlink_dump_timeout
 __ctnetlink_glue_build
 ctnetlink_glue_build
 __nfqnl_enqueue_packet
 nf_queue
 nf_hook_slow
 ip_mc_output
 ? __pfx_ip_finish_output
 ip_send_skb
 ? __pfx_dst_output
 udp_send_skb
 udp_sendmsg
 ? __pfx_ip_generic_getfrag
 sock_sendmsg

Separate the 2 cases in:
- Setting `ct->timeout` in __nf_ct_set_timeout().
- Getting `ct->timeout` in ctnetlink_dump_timeout().

Pablo appends:

Update ctnetlink to set up the timeout _after_ the IPS_CONFIRMED flag is
set on, otherwise conntrack creation via ctnetlink breaks.

Note that the problem described in this patch occurs since the
introduction of the nfnetlink_queue conntrack support, select a
sufficiently old Fixes: tag for -stable kernel to pick up this fix.

## References
- https://git.kernel.org/stable/c/73db1b8f2bb6725b7391e85aab41fdf592b3c0c1
- https://git.kernel.org/stable/c/80c5ba0078e20d926d11d0778f9a43902664ebf0
- https://git.kernel.org/stable/c/f612ae1ab4793701caf39386fb3b7f4b3ef44e48
- https://git.kernel.org/stable/c/ff5e4ac8dd7be7f1faba955c5779a68571eeb0f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53635.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53635
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
