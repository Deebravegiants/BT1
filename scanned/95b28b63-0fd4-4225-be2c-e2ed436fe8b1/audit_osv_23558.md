# [M] ath11k: Fix frames flush failure caused by deadlock

## Summary
Severity: Medium
Advisory: CVE-2022-49123
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49123
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ath11k: Fix frames flush failure caused by deadlock

We are seeing below warnings:

kernel: [25393.301506] ath11k_pci 0000:01:00.0: failed to flush mgmt transmit queue 0
kernel: [25398.421509] ath11k_pci 0000:01:00.0: failed to flush mgmt transmit queue 0
kernel: [25398.421831] ath11k_pci 0000:01:00.0: dropping mgmt frame for vdev 0, is_started 0

this means ath11k fails to flush mgmt. frames because wmi_mgmt_tx_work
has no chance to run in 5 seconds.

By setting /proc/sys/kernel/hung_task_timeout_secs to 20 and increasing
ATH11K_FLUSH_TIMEOUT to 50 we get below warnings:

kernel: [  120.763160] INFO: task wpa_supplicant:924 blocked for more than 20 seconds.
kernel: [  120.763169]       Not tainted 5.10.90 #12
kernel: [  120.763177] "echo 0 > /proc/sys/kernel/hung_task_timeout_secs" disables this message.
kernel: [  120.763186] task:wpa_supplicant  state:D stack:    0 pid:  924 ppid:     1 flags:0x000043a0
kernel: [  120.763201] Call Trace:
kernel: [  120.763214]  __schedule+0x785/0x12fa
kernel: [  120.763224]  ? lockdep_hardirqs_on_prepare+0xe2/0x1bb
kernel: [  120.763242]  schedule+0x7e/0xa1
kernel: [  120.763253]  schedule_timeout+0x98/0xfe
kernel: [  120.763266]  ? run_local_timers+0x4a/0x4a
kernel: [  120.763291]  ath11k_mac_flush_tx_complete+0x197/0x2b1 [ath11k 13c3a9bf37790f4ac8103b3decf7ab4008ac314a]
kernel: [  120.763306]  ? init_wait_entry+0x2e/0x2e
kernel: [  120.763343]  __ieee80211_flush_queues+0x167/0x21f [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763378]  __ieee80211_recalc_idle+0x105/0x125 [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763411]  ieee80211_recalc_idle+0x14/0x27 [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763441]  ieee80211_free_chanctx+0x77/0xa2 [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763473]  __ieee80211_vif_release_channel+0x100/0x131 [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763540]  ieee80211_vif_release_channel+0x66/0x81 [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763572]  ieee80211_destroy_auth_data+0xa3/0xe6 [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763612]  ieee80211_mgd_deauth+0x178/0x29b [mac80211 335da900954f1c5ea7f1613d92088ce83342042c]
kernel: [  120.763654]  cfg80211_mlme_deauth+0x1a8/0x22c [cfg80211 8945aa5bc2af5f6972336665d8ad6f9c191ad5be]
kernel: [  120.763697]  nl80211_deauthenticate+0xfa/0x123 [cfg80211 8945aa5bc2af5f6972336665d8ad6f9c191ad5be]
kernel: [  120.763715]  genl_rcv_msg+0x392/0x3c2
kernel: [  120.763750]  ? nl80211_associate+0x432/0x432 [cfg80211 8945aa5bc2af5f6972336665d8ad6f9c191ad5be]
kernel: [  120.763782]  ? nl80211_associate+0x432/0x432 [cfg80211 8945aa5bc2af5f6972336665d8ad6f9c191ad5be]
kernel: [  120.763802]  ? genl_rcv+0x36/0x36
kernel: [  120.763814]  netlink_rcv_skb+0x89/0xf7
kernel: [  120.763829]  genl_rcv+0x28/0x36
kernel: [  120.763840]  netlink_unicast+0x179/0x24b
kernel: [  120.763854]  netlink_sendmsg+0x393/0x401
kernel: [  120.763872]  sock_sendmsg+0x72/0x76
kernel: [  120.763886]  ____sys_sendmsg+0x170/0x1e6
kernel: [  120.763897]  ? copy_msghdr_from_user+0x7a/0xa2
kernel: [  120.763914]  ___sys_sendmsg+0x95/0xd1
kernel: [  120.763940]  __sys_sendmsg+0x85/0xbf
kernel: [  120.763956]  do_syscall_64+0x43/0x55
kernel: [  120.763966]  entry_SYSCALL_64_after_hwframe+0x44/0xa9
kernel: [  120.763977] RIP: 0033:0x79089f3fcc83
kernel: [  120.763986] RSP: 002b:00007ffe604f0508 EFLAGS: 00000246 ORIG_RAX: 000000000000002e
kernel: [  120.763997] RAX: ffffffffffffffda RBX: 000059b40e987690 RCX: 000079089f3fcc83
kernel: [  120.764006] RDX: 0000000000000000 RSI: 00007ffe604f0558 RDI: 0000000000000009
kernel: [  120.764014] RBP: 00007ffe604f0540 R08: 0000000000000004 R09: 0000000000400000
kernel: [  120.764023] R10: 00007ffe604f0638 R11: 0000000000000246 R12: 000059b40ea04980
kernel: [  120.764032] R13: 00007ffe604
---truncated---

## References
- https://git.kernel.org/stable/c/261b07519518bd14cb168b287b17e1d195f8d0c8
- https://git.kernel.org/stable/c/33e723dc054edfc94da90eecca3b72cb424ce4a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49123.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
