# [H] wifi: ath12k: Prevent sending WMI commands to firmware during firmware crash

## Summary
Severity: High
Advisory: CVE-2025-38291
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38291
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: Prevent sending WMI commands to firmware during firmware crash

Currently, we encounter the following kernel call trace when a firmware
crash occurs. This happens because the host sends WMI commands to the
firmware while it is in recovery, causing the commands to fail and
resulting in the kernel call trace.

Set the ATH12K_FLAG_CRASH_FLUSH and ATH12K_FLAG_RECOVERY flags when the
host driver receives the firmware crash notification from MHI. This
prevents sending WMI commands to the firmware during recovery.

Call Trace:
 <TASK>
 dump_stack_lvl+0x75/0xc0
 register_lock_class+0x6be/0x7a0
 ? __lock_acquire+0x644/0x19a0
 __lock_acquire+0x95/0x19a0
 lock_acquire+0x265/0x310
 ? ath12k_ce_send+0xa2/0x210 [ath12k]
 ? find_held_lock+0x34/0xa0
 ? ath12k_ce_send+0x56/0x210 [ath12k]
 _raw_spin_lock_bh+0x33/0x70
 ? ath12k_ce_send+0xa2/0x210 [ath12k]
 ath12k_ce_send+0xa2/0x210 [ath12k]
 ath12k_htc_send+0x178/0x390 [ath12k]
 ath12k_wmi_cmd_send_nowait+0x76/0xa0 [ath12k]
 ath12k_wmi_cmd_send+0x62/0x190 [ath12k]
 ath12k_wmi_pdev_bss_chan_info_request+0x62/0xc0 [ath1
 ath12k_mac_op_get_survey+0x2be/0x310 [ath12k]
 ieee80211_dump_survey+0x99/0x240 [mac80211]
 nl80211_dump_survey+0xe7/0x470 [cfg80211]
 ? kmalloc_reserve+0x59/0xf0
 genl_dumpit+0x24/0x70
 netlink_dump+0x177/0x360
 __netlink_dump_start+0x206/0x280
 genl_family_rcv_msg_dumpit.isra.22+0x8a/0xe0
 ? genl_family_rcv_msg_attrs_parse.isra.23+0xe0/0xe0
 ? genl_op_lock.part.12+0x10/0x10
 ? genl_dumpit+0x70/0x70
 genl_rcv_msg+0x1d0/0x290
 ? nl80211_del_station+0x330/0x330 [cfg80211]
 ? genl_get_cmd_both+0x50/0x50
 netlink_rcv_skb+0x4f/0x100
 genl_rcv+0x1f/0x30
 netlink_unicast+0x1b6/0x260
 netlink_sendmsg+0x31a/0x450
 __sock_sendmsg+0xa8/0xb0
 ____sys_sendmsg+0x1e4/0x260
 ___sys_sendmsg+0x89/0xe0
 ? local_clock_noinstr+0xb/0xc0
 ? rcu_is_watching+0xd/0x40
 ? kfree+0x1de/0x370
 ? __sys_sendmsg+0x7a/0xc0

Tested-on: QCN9274 hw2.0 PCI WLAN.WBE.1.4.1-00199-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/2563069baf243cadc76dc64d9085606742c4b282
- https://git.kernel.org/stable/c/e9e094a9734ea3bd4d4d117c915ccf129ac61ba1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38291.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38291
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
