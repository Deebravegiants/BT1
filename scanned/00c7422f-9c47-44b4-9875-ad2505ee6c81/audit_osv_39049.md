# [H] net/mlx5e: RX, Fix XDP multi-buf frag counting for legacy RQ

## Summary
Severity: High
Advisory: CVE-2026-43464
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43464
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: RX, Fix XDP multi-buf frag counting for legacy RQ

XDP multi-buf programs can modify the layout of the XDP buffer when the
program calls bpf_xdp_pull_data() or bpf_xdp_adjust_tail(). The
referenced commit in the fixes tag corrected the assumption in the mlx5
driver that the XDP buffer layout doesn't change during a program
execution. However, this fix introduced another issue: the dropped
fragments still need to be counted on the driver side to avoid page
fragment reference counting issues.

Such issue can be observed with the
test_xdp_native_adjst_tail_shrnk_data selftest when using a payload of
3600 and shrinking by 256 bytes (an upcoming selftest patch): the last
fragment gets released by the XDP code but doesn't get tracked by the
driver. This results in a negative pp_ref_count during page release and
the following splat:

  WARNING: include/net/page_pool/helpers.h:297 at mlx5e_page_release_fragmented.isra.0+0x4a/0x50 [mlx5_core], CPU#12: ip/3137
  Modules linked in: [...]
  CPU: 12 UID: 0 PID: 3137 Comm: ip Not tainted 6.19.0-rc3+ #12 NONE
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS rel-1.16.3-0-ga6ed6b701f0a-prebuilt.qemu.org 04/01/2014
  RIP: 0010:mlx5e_page_release_fragmented.isra.0+0x4a/0x50 [mlx5_core]
  [...]
  Call Trace:
   <TASK>
   mlx5e_dealloc_rx_wqe+0xcb/0x1a0 [mlx5_core]
   mlx5e_free_rx_descs+0x7f/0x110 [mlx5_core]
   mlx5e_close_rq+0x50/0x60 [mlx5_core]
   mlx5e_close_queues+0x36/0x2c0 [mlx5_core]
   mlx5e_close_channel+0x1c/0x50 [mlx5_core]
   mlx5e_close_channels+0x45/0x80 [mlx5_core]
   mlx5e_safe_switch_params+0x1a5/0x230 [mlx5_core]
   mlx5e_change_mtu+0xf3/0x2f0 [mlx5_core]
   netif_set_mtu_ext+0xf1/0x230
   do_setlink.isra.0+0x219/0x1180
   rtnl_newlink+0x79f/0xb60
   rtnetlink_rcv_msg+0x213/0x3a0
   netlink_rcv_skb+0x48/0xf0
   netlink_unicast+0x24a/0x350
   netlink_sendmsg+0x1ee/0x410
   __sock_sendmsg+0x38/0x60
   ____sys_sendmsg+0x232/0x280
   ___sys_sendmsg+0x78/0xb0
   __sys_sendmsg+0x5f/0xb0
   [...]
   do_syscall_64+0x57/0xc50

This patch fixes the issue by doing page frag counting on all the
original XDP buffer fragments for all relevant XDP actions (XDP_TX ,
XDP_REDIRECT and XDP_PASS). This is basically reverting to the original
counting before the commit in the fixes tag.

As frag_page is still pointing to the original tail, the nr_frags
parameter to xdp_update_skb_frags_info() needs to be calculated
in a different way to reflect the new nr_frags.

## References
- https://git.kernel.org/stable/c/03cb50e5b74fce8bf6d92b860371b66253cf0f8d
- https://git.kernel.org/stable/c/a6413e6f6c9d9bb9833324cb3753582f7bc0f2fa
- https://git.kernel.org/stable/c/c74557495efb4bd0adefdfc8678ecdbc82a06da3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43464.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43464
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
