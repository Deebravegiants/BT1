# [H] net/mlx5e: Fix "scheduling while atomic" in IPsec MAC address query

## Summary
Severity: High
Advisory: CVE-2026-43199
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43199
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix "scheduling while atomic" in IPsec MAC address query

Fix a "scheduling while atomic" bug in mlx5e_ipsec_init_macs() by
replacing mlx5_query_mac_address() with ether_addr_copy() to get the
local MAC address directly from netdev->dev_addr.

The issue occurs because mlx5_query_mac_address() queries the hardware
which involves mlx5_cmd_exec() that can sleep, but it is called from
the mlx5e_ipsec_handle_event workqueue which runs in atomic context.

The MAC address is already available in netdev->dev_addr, so no need
to query hardware. This avoids the sleeping call and resolves the bug.

Call trace:
  BUG: scheduling while atomic: kworker/u112:2/69344/0x00000200
  __schedule+0x7ab/0xa20
  schedule+0x1c/0xb0
  schedule_timeout+0x6e/0xf0
  __wait_for_common+0x91/0x1b0
  cmd_exec+0xa85/0xff0 [mlx5_core]
  mlx5_cmd_exec+0x1f/0x50 [mlx5_core]
  mlx5_query_nic_vport_mac_address+0x7b/0xd0 [mlx5_core]
  mlx5_query_mac_address+0x19/0x30 [mlx5_core]
  mlx5e_ipsec_init_macs+0xc1/0x720 [mlx5_core]
  mlx5e_ipsec_build_accel_xfrm_attrs+0x422/0x670 [mlx5_core]
  mlx5e_ipsec_handle_event+0x2b9/0x460 [mlx5_core]
  process_one_work+0x178/0x2e0
  worker_thread+0x2ea/0x430

## References
- https://git.kernel.org/stable/c/546de94e41e92e1f7dc6213615fb7c794d05db98
- https://git.kernel.org/stable/c/57957bc7f1865778ec9b1618e15515feb6df7eb4
- https://git.kernel.org/stable/c/859380694f434597407632c29f30fdb5e763e6cc
- https://git.kernel.org/stable/c/e1407fb7c337373dfaaae2445d828b0b9ae26a29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43199.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43199
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
