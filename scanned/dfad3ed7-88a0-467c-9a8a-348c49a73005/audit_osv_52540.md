# [M] CVE-2021-47558

## Summary
Severity: Medium
Advisory: CVE-2021-47558
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47558
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: Disable Tx queues when reconfiguring the interface

The Tx queues were not disabled in situations where the driver needed to
stop the interface to apply a new configuration. This could result in a
kernel panic when doing any of the 3 following actions:
* reconfiguring the number of queues (ethtool -L)
* reconfiguring the size of the ring buffers (ethtool -G)
* installing/removing an XDP program (ip l set dev ethX xdp)

Prevent the panic by making sure netif_tx_disable is called when stopping
an interface.

Without this patch, the following kernel panic can be observed when doing
any of the actions above:

Unable to handle kernel paging request at virtual address ffff80001238d040
[....]
 Call trace:
  dwmac4_set_addr+0x8/0x10
  dev_hard_start_xmit+0xe4/0x1ac
  sch_direct_xmit+0xe8/0x39c
  __dev_queue_xmit+0x3ec/0xaf0
  dev_queue_xmit+0x14/0x20
[...]
[ end trace 0000000000000002 ]---

## References
- https://git.kernel.org/stable/c/a92f0eebb8dc008b9e8c51c6f7b8c93b27a29a43
- https://git.kernel.org/stable/c/b270bfe697367776eca2e6759a71d700fb8d82a2
