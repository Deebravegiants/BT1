# [H] wifi: mt76: mt7921s: fix slab-out-of-bounds access in sdio host

## Summary
Severity: High
Advisory: CVE-2022-50701
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50701
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: mt7921s: fix slab-out-of-bounds access in sdio host

SDIO may need addtional 511 bytes to align bus operation. If the tailroom
of this skb is not big enough, we would access invalid memory region.
For low level operation, increase skb size to keep valid memory access in
SDIO host.

Error message:
[69.951] BUG: KASAN: slab-out-of-bounds in sg_copy_buffer+0xe9/0x1a0
[69.951] Read of size 64 at addr ffff88811c9cf000 by task kworker/u16:7/451
[69.951] CPU: 4 PID: 451 Comm: kworker/u16:7 Tainted: G W  OE  6.1.0-rc5 #1
[69.951] Workqueue: kvub300c vub300_cmndwork_thread [vub300]
[69.951] Call Trace:
[69.951]  <TASK>
[69.952]  dump_stack_lvl+0x49/0x63
[69.952]  print_report+0x171/0x4a8
[69.952]  kasan_report+0xb4/0x130
[69.952]  kasan_check_range+0x149/0x1e0
[69.952]  memcpy+0x24/0x70
[69.952]  sg_copy_buffer+0xe9/0x1a0
[69.952]  sg_copy_to_buffer+0x12/0x20
[69.952]  __command_write_data.isra.0+0x23c/0xbf0 [vub300]
[69.952]  vub300_cmndwork_thread+0x17f3/0x58b0 [vub300]
[69.952]  process_one_work+0x7ee/0x1320
[69.952]  worker_thread+0x53c/0x1240
[69.952]  kthread+0x2b8/0x370
[69.952]  ret_from_fork+0x1f/0x30
[69.952]  </TASK>

[69.952] Allocated by task 854:
[69.952]  kasan_save_stack+0x26/0x50
[69.952]  kasan_set_track+0x25/0x30
[69.952]  kasan_save_alloc_info+0x1b/0x30
[69.952]  __kasan_kmalloc+0x87/0xa0
[69.952]  __kmalloc_node_track_caller+0x63/0x150
[69.952]  kmalloc_reserve+0x31/0xd0
[69.952]  __alloc_skb+0xfc/0x2b0
[69.952]  __mt76_mcu_msg_alloc+0xbf/0x230 [mt76]
[69.952]  mt76_mcu_send_and_get_msg+0xab/0x110 [mt76]
[69.952]  __mt76_mcu_send_firmware.cold+0x94/0x15d [mt76]
[69.952]  mt76_connac_mcu_send_ram_firmware+0x415/0x54d [mt76_connac_lib]
[69.952]  mt76_connac2_load_ram.cold+0x118/0x4bc [mt76_connac_lib]
[69.952]  mt7921_run_firmware.cold+0x2e9/0x405 [mt7921_common]
[69.952]  mt7921s_mcu_init+0x45/0x80 [mt7921s]
[69.953]  mt7921_init_work+0xe1/0x2a0 [mt7921_common]
[69.953]  process_one_work+0x7ee/0x1320
[69.953]  worker_thread+0x53c/0x1240
[69.953]  kthread+0x2b8/0x370
[69.953]  ret_from_fork+0x1f/0x30
[69.953] The buggy address belongs to the object at ffff88811c9ce800
             which belongs to the cache kmalloc-2k of size 2048
[69.953] The buggy address is located 0 bytes to the right of
             2048-byte region [ffff88811c9ce800, ffff88811c9cf000)

[69.953] Memory state around the buggy address:
[69.953]  ffff88811c9cef00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
[69.953]  ffff88811c9cef80: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
[69.953] >ffff88811c9cf000: fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc
[69.953]                    ^
[69.953]  ffff88811c9cf080: fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc
[69.953]  ffff88811c9cf100: fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc fc

## References
- https://git.kernel.org/stable/c/0b358e36433d2c46a65488a146bf8b4623fc5bbb
- https://git.kernel.org/stable/c/8b5174a7f25d03df0ffa171ff86de383a89e8e89
- https://git.kernel.org/stable/c/aec4cf2ea0797e28f18f8dbe01943a56d987fe56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50701.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50701
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
