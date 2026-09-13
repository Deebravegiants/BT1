# [H] mptcp: pm: Fix uaf in __timer_delete_sync

## Summary
Severity: High
Advisory: CVE-2024-46858
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46858
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.111, >=6.2.0 <6.6.52, >=6.7.0 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: pm: Fix uaf in __timer_delete_sync

There are two paths to access mptcp_pm_del_add_timer, result in a race
condition:

     CPU1				CPU2
     ====                               ====
     net_rx_action
     napi_poll                          netlink_sendmsg
     __napi_poll                        netlink_unicast
     process_backlog                    netlink_unicast_kernel
     __netif_receive_skb                genl_rcv
     __netif_receive_skb_one_core       netlink_rcv_skb
     NF_HOOK                            genl_rcv_msg
     ip_local_deliver_finish            genl_family_rcv_msg
     ip_protocol_deliver_rcu            genl_family_rcv_msg_doit
     tcp_v4_rcv                         mptcp_pm_nl_flush_addrs_doit
     tcp_v4_do_rcv                      mptcp_nl_remove_addrs_list
     tcp_rcv_established                mptcp_pm_remove_addrs_and_subflows
     tcp_data_queue                     remove_anno_list_by_saddr
     mptcp_incoming_options             mptcp_pm_del_add_timer
     mptcp_pm_del_add_timer             kfree(entry)

In remove_anno_list_by_saddr(running on CPU2), after leaving the critical
zone protected by "pm.lock", the entry will be released, which leads to the
occurrence of uaf in the mptcp_pm_del_add_timer(running on CPU1).

Keeping a reference to add_timer inside the lock, and calling
sk_stop_timer_sync() with this reference, instead of "entry->add_timer".

Move list_del(&entry->list) to mptcp_pm_del_add_timer and inside the pm lock,
do not directly access any members of the entry outside the pm lock, which
can avoid similar "entry->x" uaf.

## References
- https://git.kernel.org/stable/c/0e7814b028cd50b3ff79659d23dfa9da6a1e75e1
- https://git.kernel.org/stable/c/12134a652b0a10064844ea235173e70246eba6dc
- https://git.kernel.org/stable/c/3554482f4691571fc4b5490c17ae26896e62171c
- https://git.kernel.org/stable/c/6452b162549c7f9ef54655d3fb9977b9192e6e5b
- https://git.kernel.org/stable/c/67409b358500c71632116356a0b065f112d7b707
- https://git.kernel.org/stable/c/b4cd80b0338945a94972ac3ed54f8338d2da2076
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46858.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
