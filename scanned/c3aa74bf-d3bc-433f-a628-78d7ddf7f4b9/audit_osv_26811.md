# [H] wifi: rtw88: use work to update rate to avoid RCU warning

## Summary
Severity: High
Advisory: CVE-2023-54071
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54071
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw88: use work to update rate to avoid RCU warning

The ieee80211_ops::sta_rc_update must be atomic, because
ieee80211_chan_bw_change() holds rcu_read lock while calling
drv_sta_rc_update(), so create a work to do original things.

 Voluntary context switch within RCU read-side critical section!
 WARNING: CPU: 0 PID: 4621 at kernel/rcu/tree_plugin.h:318
 rcu_note_context_switch+0x571/0x5d0
 CPU: 0 PID: 4621 Comm: kworker/u16:2 Tainted: G        W  OE
 Workqueue: phy3 ieee80211_chswitch_work [mac80211]
 RIP: 0010:rcu_note_context_switch+0x571/0x5d0
 Call Trace:
  <TASK>
  __schedule+0xb0/0x1460
  ? __mod_timer+0x116/0x360
  schedule+0x5a/0xc0
  schedule_timeout+0x87/0x150
  ? trace_raw_output_tick_stop+0x60/0x60
  wait_for_completion_timeout+0x7b/0x140
  usb_start_wait_urb+0x82/0x160 [usbcore
  usb_control_msg+0xe3/0x140 [usbcore
  rtw_usb_read+0x88/0xe0 [rtw_usb
  rtw_usb_read8+0xf/0x10 [rtw_usb
  rtw_fw_send_h2c_command+0xa0/0x170 [rtw_core
  rtw_fw_send_ra_info+0xc9/0xf0 [rtw_core
  drv_sta_rc_update+0x7c/0x160 [mac80211
  ieee80211_chan_bw_change+0xfb/0x110 [mac80211
  ieee80211_change_chanctx+0x38/0x130 [mac80211
  ieee80211_vif_use_reserved_switch+0x34e/0x900 [mac80211
  ieee80211_link_use_reserved_context+0x88/0xe0 [mac80211
  ieee80211_chswitch_work+0x95/0x170 [mac80211
  process_one_work+0x201/0x410
  worker_thread+0x4a/0x3b0
  ? process_one_work+0x410/0x410
  kthread+0xe1/0x110
  ? kthread_complete_and_exit+0x20/0x20
  ret_from_fork+0x1f/0x30
  </TASK>

## References
- https://git.kernel.org/stable/c/107677a8f43521e33e4a653e50fdf55ba622a4ce
- https://git.kernel.org/stable/c/bcafcb959a57a6890e900199690c5fc47da1a304
- https://git.kernel.org/stable/c/dd3af22323e79a2ffabed366db20aab83716fe6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54071.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54071
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
