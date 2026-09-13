# [M] wifi: mt76: mt7921: fix kernel panic due to null pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2025-22032
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22032
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7921: fix kernel panic due to null pointer dereference

Address a kernel panic caused by a null pointer dereference in the
`mt792x_rx_get_wcid` function. The issue arises because the `deflink` structure
is not properly initialized with the `sta` context. This patch ensures that the
`deflink` structure is correctly linked to the `sta` context, preventing the
null pointer dereference.

 BUG: kernel NULL pointer dereference, address: 0000000000000400
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: Oops: 0000 [#1] PREEMPT SMP NOPTI
 CPU: 0 UID: 0 PID: 470 Comm: mt76-usb-rx phy Not tainted 6.12.13-gentoo-dist #1
 Hardware name:  /AMD HUDSON-M1, BIOS 4.6.4 11/15/2011
 RIP: 0010:mt792x_rx_get_wcid+0x48/0x140 [mt792x_lib]
 RSP: 0018:ffffa147c055fd98 EFLAGS: 00010202
 RAX: 0000000000000000 RBX: ffff8e9ecb652000 RCX: 0000000000000000
 RDX: 0000000000000000 RSI: 0000000000000001 RDI: ffff8e9ecb652000
 RBP: 0000000000000685 R08: ffff8e9ec6570000 R09: 0000000000000000
 R10: ffff8e9ecd2ca000 R11: ffff8e9f22a217c0 R12: 0000000038010119
 R13: 0000000080843801 R14: ffff8e9ec6570000 R15: ffff8e9ecb652000
 FS:  0000000000000000(0000) GS:ffff8e9f22a00000(0000) knlGS:0000000000000000
 CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 0000000000000400 CR3: 000000000d2ea000 CR4: 00000000000006f0
 Call Trace:
  <TASK>
  ? __die_body.cold+0x19/0x27
  ? page_fault_oops+0x15a/0x2f0
  ? search_module_extables+0x19/0x60
  ? search_bpf_extables+0x5f/0x80
  ? exc_page_fault+0x7e/0x180
  ? asm_exc_page_fault+0x26/0x30
  ? mt792x_rx_get_wcid+0x48/0x140 [mt792x_lib]
  mt7921_queue_rx_skb+0x1c6/0xaa0 [mt7921_common]
  mt76u_alloc_queues+0x784/0x810 [mt76_usb]
  ? __pfx___mt76_worker_fn+0x10/0x10 [mt76]
  __mt76_worker_fn+0x4f/0x80 [mt76]
  kthread+0xd2/0x100
  ? __pfx_kthread+0x10/0x10
  ret_from_fork+0x34/0x50
  ? __pfx_kthread+0x10/0x10
  ret_from_fork_asm+0x1a/0x30
  </TASK>
 ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/0cfea60966e4b1239d20bebf02258295e189e82a
- https://git.kernel.org/stable/c/5a57f8eb2a17d469d65cd1186cea26b798221d4a
- https://git.kernel.org/stable/c/adc3fd2a2277b7cc0b61692463771bf9bd298036
- https://git.kernel.org/stable/c/effec50381991bc067acf4b3351a57831c74d27f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22032.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22032
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
