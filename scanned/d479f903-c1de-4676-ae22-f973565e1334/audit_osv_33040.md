# [H] wifi: rtl818x: Kill URBs before clearing tx status queue

## Summary
Severity: High
Advisory: CVE-2025-38604
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38604
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtl818x: Kill URBs before clearing tx status queue

In rtl8187_stop() move the call of usb_kill_anchored_urbs() before clearing
b_tx_status.queue. This change prevents callbacks from using already freed
skb due to anchor was not killed before freeing such skb.

 BUG: kernel NULL pointer dereference, address: 0000000000000080
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: Oops: 0000 [#1] SMP NOPTI
 CPU: 7 UID: 0 PID: 0 Comm: swapper/7 Not tainted 6.15.0 #8 PREEMPT(voluntary)
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 0.0.0 02/06/2015
 RIP: 0010:ieee80211_tx_status_irqsafe+0x21/0xc0 [mac80211]
 Call Trace:
  <IRQ>
  rtl8187_tx_cb+0x116/0x150 [rtl8187]
  __usb_hcd_giveback_urb+0x9d/0x120
  usb_giveback_urb_bh+0xbb/0x140
  process_one_work+0x19b/0x3c0
  bh_worker+0x1a7/0x210
  tasklet_action+0x10/0x30
  handle_softirqs+0xf0/0x340
  __irq_exit_rcu+0xcd/0xf0
  common_interrupt+0x85/0xa0
  </IRQ>

Tested on RTL8187BvE device.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/14ca6952691fa8cc91e7644512e6ff24a595283f
- https://git.kernel.org/stable/c/16d8fd74dbfca0ea58645cd2fca13be10cae3cdd
- https://git.kernel.org/stable/c/7858a95566f4ebf59524666683d2dcdba3fca968
- https://git.kernel.org/stable/c/789415771422f4fb9f444044f86ecfaec55df1bd
- https://git.kernel.org/stable/c/81cfe34d0630de4e23ae804dcc08fb6f861dc37d
- https://git.kernel.org/stable/c/8c767727f331fb9455b0f81daad832b5925688cb
- https://git.kernel.org/stable/c/c51a45ad9070a6d296174fcbe5c466352836c12b
- https://git.kernel.org/stable/c/c73c773b09e313278f9b960303a2809b8440bac6
- https://git.kernel.org/stable/c/e64732ebff9e24258e7326f07adbe2f2b990daf8
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38604.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38604
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
