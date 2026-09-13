# [H] wifi: wilc1000: fix RCU usage in connect path

## Summary
Severity: High
Advisory: CVE-2024-27053
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27053
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wilc1000: fix RCU usage in connect path

With lockdep enabled, calls to the connect function from cfg802.11 layer
lead to the following warning:

=============================
WARNING: suspicious RCU usage
6.7.0-rc1-wt+ #333 Not tainted
-----------------------------
drivers/net/wireless/microchip/wilc1000/hif.c:386
suspicious rcu_dereference_check() usage!
[...]
stack backtrace:
CPU: 0 PID: 100 Comm: wpa_supplicant Not tainted 6.7.0-rc1-wt+ #333
Hardware name: Atmel SAMA5
 unwind_backtrace from show_stack+0x18/0x1c
 show_stack from dump_stack_lvl+0x34/0x48
 dump_stack_lvl from wilc_parse_join_bss_param+0x7dc/0x7f4
 wilc_parse_join_bss_param from connect+0x2c4/0x648
 connect from cfg80211_connect+0x30c/0xb74
 cfg80211_connect from nl80211_connect+0x860/0xa94
 nl80211_connect from genl_rcv_msg+0x3fc/0x59c
 genl_rcv_msg from netlink_rcv_skb+0xd0/0x1f8
 netlink_rcv_skb from genl_rcv+0x2c/0x3c
 genl_rcv from netlink_unicast+0x3b0/0x550
 netlink_unicast from netlink_sendmsg+0x368/0x688
 netlink_sendmsg from ____sys_sendmsg+0x190/0x430
 ____sys_sendmsg from ___sys_sendmsg+0x110/0x158
 ___sys_sendmsg from sys_sendmsg+0xe8/0x150
 sys_sendmsg from ret_fast_syscall+0x0/0x1c

This warning is emitted because in the connect path, when trying to parse
target BSS parameters, we dereference a RCU pointer whithout being in RCU
critical section.
Fix RCU dereference usage by moving it to a RCU read critical section. To
avoid wrapping the whole wilc_parse_join_bss_param under the critical
section, just use the critical section to copy ies data

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/205c50306acf58a335eb19fa84e40140f4fe814f
- https://git.kernel.org/stable/c/4bfd20d5f5c62b5495d6c0016ee6933bd3add7ce
- https://git.kernel.org/stable/c/5800ec78775c0cd646f71eb9bf8402fb794807de
- https://git.kernel.org/stable/c/745003b5917b610352f52fe0d11ef658d6471ec2
- https://git.kernel.org/stable/c/b4bbf38c350acb6500cbe667b1e2e68f896e4b38
- https://git.kernel.org/stable/c/d80fc436751cfa6b02a8eda74eb6cce7dadfe5a2
- https://git.kernel.org/stable/c/dd50d3ead6e3707bb0a5df7cc832730c93ace3a7
- https://git.kernel.org/stable/c/e556006de4ea93abe2b46cba202a2556c544b8b2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27053.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
