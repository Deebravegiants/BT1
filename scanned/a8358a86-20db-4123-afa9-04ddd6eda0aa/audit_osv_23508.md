# [H] wifi: mac8021: fix possible oob access in ieee80211_get_rate_duration

## Summary
Severity: High
Advisory: CVE-2022-49022
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49022
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac8021: fix possible oob access in ieee80211_get_rate_duration

Fix possible out-of-bound access in ieee80211_get_rate_duration routine
as reported by the following UBSAN report:

UBSAN: array-index-out-of-bounds in net/mac80211/airtime.c:455:47
index 15 is out of range for type 'u16 [12]'
CPU: 2 PID: 217 Comm: kworker/u32:10 Not tainted 6.1.0-060100rc3-generic
Hardware name: Acer Aspire TC-281/Aspire TC-281, BIOS R01-A2 07/18/2017
Workqueue: mt76 mt76u_tx_status_data [mt76_usb]
Call Trace:
 <TASK>
 show_stack+0x4e/0x61
 dump_stack_lvl+0x4a/0x6f
 dump_stack+0x10/0x18
 ubsan_epilogue+0x9/0x43
 __ubsan_handle_out_of_bounds.cold+0x42/0x47
ieee80211_get_rate_duration.constprop.0+0x22f/0x2a0 [mac80211]
 ? ieee80211_tx_status_ext+0x32e/0x640 [mac80211]
 ieee80211_calc_rx_airtime+0xda/0x120 [mac80211]
 ieee80211_calc_tx_airtime+0xb4/0x100 [mac80211]
 mt76x02_send_tx_status+0x266/0x480 [mt76x02_lib]
 mt76x02_tx_status_data+0x52/0x80 [mt76x02_lib]
 mt76u_tx_status_data+0x67/0xd0 [mt76_usb]
 process_one_work+0x225/0x400
 worker_thread+0x50/0x3e0
 ? process_one_work+0x400/0x400
 kthread+0xe9/0x110
 ? kthread_complete_and_exit+0x20/0x20
 ret_from_fork+0x22/0x30

## References
- https://git.kernel.org/stable/c/0184ede0ec61b9cd075babfaa45081b1bf322234
- https://git.kernel.org/stable/c/3e8f7abcc3473bc9603323803aeaed4ffcc3a2ab
- https://git.kernel.org/stable/c/59b54f0563b6546c94bdb6823d3b382c75407019
- https://git.kernel.org/stable/c/f0fcad4c7201ecfaa17357f4ce0c50b4708df22d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49022.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49022
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
