# [H] net/mlx5e: TC, skip peer flow cleanup when LAG seq is unavailable

## Summary
Severity: High
Advisory: CVE-2026-72344
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72344
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: TC, skip peer flow cleanup when LAG seq is unavailable

mlx5_lag_get_dev_seq() will return error when the peer isn't in the LAG
or when no device is marked as master. Result bad memory access and kernel
crash[1].

Hence, skip the peer when lookup fails.

Note: In case there are peer flows, they are cleaned before LAG cleared
the master mark.

[1]
RIP: 0010:mlx5e_tc_del_fdb_peers_flow+0x3d/0x350 [mlx5_core]
Call Trace:
 <TASK>
 mlx5e_tc_clean_fdb_peer_flows+0xc1/0x130 [mlx5_core]
 mlx5_esw_offloads_unpair+0x3a/0x400 [mlx5_core]
 mlx5_esw_offloads_devcom_event+0xee/0x360 [mlx5_core]
 mlx5_devcom_send_event+0x7a/0x140 [mlx5_core]
 mlx5_esw_offloads_devcom_cleanup+0x2f/0x90 [mlx5_core]
 mlx5e_tc_esw_cleanup+0x28/0xf0 [mlx5_core]
 mlx5e_rep_tc_cleanup+0x19/0x30 [mlx5_core]
 mlx5e_cleanup_uplink_rep_tx+0x36/0x40 [mlx5_core]
 mlx5e_cleanup_rep_tx+0x55/0x60 [mlx5_core]
 mlx5e_detach_netdev+0x96/0xf0 [mlx5_core]
 mlx5e_netdev_change_profile+0x5b/0x120 [mlx5_core]
 mlx5e_netdev_attach_nic_profile+0x1b/0x30 [mlx5_core]
 mlx5e_vport_rep_unload+0xdd/0x110 [mlx5_core]
 __esw_offloads_unload_rep+0x81/0xb0 [mlx5_core]
 mlx5_eswitch_unregister_vport_reps+0x1d7/0x220 [mlx5_core]
 mlx5e_rep_remove+0x22/0x30 [mlx5_core]
 device_release_driver_internal+0x194/0x1f0
 bus_remove_device+0xe8/0x1b0
 device_del+0x159/0x3c0
 mlx5_rescan_drivers_locked+0xbc/0x2d0 [mlx5_core]
 mlx5_unregister_device+0x54/0x80 [mlx5_core]
 mlx5_uninit_one+0x73/0x130 [mlx5_core]
 remove_one+0x78/0xe0 [mlx5_core]
 pci_device_remove+0x39/0xa0

## References
- https://git.kernel.org/stable/c/5a95aa0198af75047d98fb72950642c89dab770f
- https://git.kernel.org/stable/c/7bed4af0ced82948d660205efecd551ef8bc3912
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72344.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72344
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
