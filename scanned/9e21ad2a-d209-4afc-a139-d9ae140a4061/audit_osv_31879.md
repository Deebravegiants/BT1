# [H] net: gso: fix ownership in __udp_gso_segment

## Summary
Severity: High
Advisory: CVE-2025-21926
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21926
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: gso: fix ownership in __udp_gso_segment

In __udp_gso_segment the skb destructor is removed before segmenting the
skb but the socket reference is kept as-is. This is an issue if the
original skb is later orphaned as we can hit the following bug:

  kernel BUG at ./include/linux/skbuff.h:3312!  (skb_orphan)
  RIP: 0010:ip_rcv_core+0x8b2/0xca0
  Call Trace:
   ip_rcv+0xab/0x6e0
   __netif_receive_skb_one_core+0x168/0x1b0
   process_backlog+0x384/0x1100
   __napi_poll.constprop.0+0xa1/0x370
   net_rx_action+0x925/0xe50

The above can happen following a sequence of events when using
OpenVSwitch, when an OVS_ACTION_ATTR_USERSPACE action precedes an
OVS_ACTION_ATTR_OUTPUT action:

1. OVS_ACTION_ATTR_USERSPACE is handled (in do_execute_actions): the skb
   goes through queue_gso_packets and then __udp_gso_segment, where its
   destructor is removed.
2. The segments' data are copied and sent to userspace.
3. OVS_ACTION_ATTR_OUTPUT is handled (in do_execute_actions) and the
   same original skb is sent to its path.
4. If it later hits skb_orphan, we hit the bug.

Fix this by also removing the reference to the socket in
__udp_gso_segment.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/01a83237644d6822bc7df2c5564fc81b0df84358
- https://git.kernel.org/stable/c/084819b0d8b1bd433b90142371eb9450d657f8ca
- https://git.kernel.org/stable/c/455217ac9db0cf9349b3933664355e907bb1a569
- https://git.kernel.org/stable/c/9f28205ddb76e86cac418332e952241d85fed0dc
- https://git.kernel.org/stable/c/a2d1cca955ed34873e524cc2e6e885450d262f05
- https://git.kernel.org/stable/c/c32da44cc9298eaa6109e3fc2c2b4e07cc4bf11b
- https://git.kernel.org/stable/c/e8db70537878e1bb3fd83e5abcc6feefc0587828
- https://git.kernel.org/stable/c/ee01b2f2d7d0010787c2343463965bbc283a497f
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21926.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
