# [H] wifi: rtw89: Correct data type for scan index to avoid infinite loop

## Summary
Severity: High
Advisory: CVE-2026-74411
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74411
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw89: Correct data type for scan index to avoid infinite loop

A kernel soft lockup was observed during Wi-Fi scanning on the 6GHz band.
The CPU becomes stuck in rtw89_hw_scan_add_chan_ax for over 20 seconds,
leading to a system panic.

RIP points to 0f b6 c3 (movzbl %bl, %eax), which zero-extends
the low 8 bits of RBX into RAX.
RBX (the counter i) has reached a huge value: 0x137466a1.

  watchdog: BUG: soft lockup - CPU#2 stuck for 26s! [kworker/u16:4:6124]
  Workqueue: events_unbound cfg80211_wiphy_work [cfg80211]
  RIP: 0010:rtw89_hw_scan_add_chan_ax+0xb3/0x6e0 [rtw89_core]
  Code: a0 48 89 45 a8 44 89 6d 9c 44 89 75 98 eb 29 66 66 2e 0f 1f
  84 00 00 00 00 00 66 66 2e 0f 1f 84 00 00 00 00 00 66 90 83 c3 01
  <0f> b6 c3 41 3b 44 24 74 0f 83 0b 02 00 00 0f b6 c3 48 8d 14 80 49
  RSP: 0018:ffffcb48cbaa39f8 EFLAGS: 00000202
  RAX: 0000000000000005 RBX: 00000000137466a1 RCX: 0000000000000000
  RDX: ffff89ffc9d851a8 RSI: 0000000000004f0d RDI: 0000000096af0130
  RBP: ffffcb48cbaa3a60 R08: 0000000000000000 R09: ffff8a00b7502080
  R10: ffff8a00b75ff600 R11: 0000000000000000 R12: ffff89ffc7553870
  R13: ffff8a00b7ac8f19 R14: ffff8a00b75020d8 R15: ffff89ffc3d54d80
  FS:  0000000000000000(0000) GS:ffff8a014f962000(0000)
  knlGS:0000000000000000
  CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
  CR2: 00007558d7f9f4c4 CR3: 0000000178040001 CR4: 00000000001706f0
  Call Trace:
   <TASK>
   rtw89_hw_scan_prep_chan_list_ax+0x8a/0x400 [rtw89_core]
   rtw89_hw_scan_start+0x546/0x8a0 [rtw89_core]
   ? rtw89_fw_h2c_default_cmac_tbl+0x13c/0x1f0 [rtw89_core]
   rtw89_ops_hw_scan+0xae/0x120 [rtw89_core]
   drv_hw_scan+0xbb/0x180 [mac80211]
   __ieee80211_start_scan+0x2fc/0x750 [mac80211]
   ieee80211_request_scan+0xe/0x20 [mac80211]
   ieee80211_scan+0x123/0x190 [mac80211]
   rdev_scan+0x40/0x110 [cfg80211]
   cfg80211_scan_6ghz+0x5a1/0xa30 [cfg80211]

By objdump with source:

	for (i = 0; i < req->n_6ghz_params; i++) {
   5fbc0:	83 c3 01             	add    $0x1,%ebx --> i++
   5fbc3:	0f b6 c3             	movzbl %bl,%eax  --> get counter
   fbc6:	41 3b 44 24 74       	cmp    0x74(%r12),%eax

   * RBX: 00000000137466a1 -> %bl = a1 -> EAX = 000000a1 (161)

## References
- https://git.kernel.org/stable/c/05d46e30303275f21f13c951166d39c85df976d4
- https://git.kernel.org/stable/c/08fdcb529df6df3562dd2b0035f88dd5be8b3c68
- https://git.kernel.org/stable/c/140fa699cfd0e18ab2f1497acd951fb3548610f5
- https://git.kernel.org/stable/c/7a1ab5fdcae896e20ca6d68fa0fbd2816cb7471f
- https://git.kernel.org/stable/c/966fbed4b4463fbcb49c5becf3f86eae776861bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74411.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
